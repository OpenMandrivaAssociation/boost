%define cmake_build 0

%if %cmake_build
%define cmake_pl 0
%else
%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")
%endif

# From the version 13 of Fedora, the Boost libraries are delivered
# with sonames equal to the Boost version (e.g., 1.41.0). 
%define	libname %mklibname boost %{version}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s

Summary:	Portable C++ libraries
Name:		boost
Version:	1.42.0
Release:	%mkrel 1
License:	Boost
Group:		Development/C++
URL:		http://boost.org/
%if %cmake_build
Source0:	http://sodium.resophonic.com/boost-cmake/%{version}.cmake%{cmake_pl}/boost-%{version}.cmake%{cmake_pl}.tar.gz
BuildRequires:	cmake
%else
Source0:	http://umn.dl.sourceforge.net/sourceforge/boost/boost_%{packver}.tar.bz2
BuildRequires:	boost-jam
%endif
# (anssi) in bjam mode, use CXXFLAGS when optimization=speed
Patch0:		boost-use-cxxflags.patch
BuildRequires:	bzip2-devel
BuildRequires:	python-devel
BuildRequires:	zlib-devel
BuildRequires:	icu-devel
#BuildRequires:	openmpi-devel
BuildRequires:	expat-devel
BuildRequires:	doxygen xsltproc
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

%define boostlibs date_time filesystem graph iostreams math_c99 math_c99f math_c99l math_tr1 math_tr1f math_tr1l prg_exec_monitor program_options python regex serialization signals system thread unit_test_framework wave wserialization

# (Anssi 01/2010) dashes are converted to underscores for macros ($lib2);
# The sed script adds _ when library name ends in number.
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%global libname$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') %{version}
%%package -n %%{libname$lib2}
Summary:	Boost $lib shared library
# no one should require this, but provided anyway for maximum compatibility:
Provides:	boost = %version-%release
Group:		System/Libraries
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string. If necessary in the future, do
# the same split for %%files as well.
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{libname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
%%files -n %%{libname$lib2}
%%defattr(-,root,root)
%%doc LICENSE_1_0.txt
%{_libdir}/libboost_$lib.so.%{version}
EOF
done)}

%package -n	%{libnamedevel}
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Requires:	%{expand:%(for lib in %boostlibs; do echo -n "%%{libname${lib/-/_}} = %{version}-%{release} "; done)}
Obsoletes:	%{mklibname boost 1}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n	%{libnamedevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains headers and shared library
symlinks needed for Boost development.

%package -n     %{libnamedevel}-doc
Summary:        The libraries and headers needed for Boost development
Group:          Development/C++
Provides:       %{name}-devel-doc = %{version}-%{release}
Conflicts:      %{_lib}boost-devel < 1.41.0

%description -n %{libnamedevel}-doc
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains documentation needed for Boost
development.

%package -n	%{libnamestaticdevel}
Summary:	Static libraries for Boost development
Group:		Development/C++
Requires:	%{libnamedevel} = %{version}-%{release}
Obsoletes:	%{mklibname boost 1}-static-devel < %{version}-%{release}
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n	%{libnamestaticdevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the static libraries
needed for Boost development.

%package -n	%{name}-examples
Summary:	The examples for the Boost libraries
Group:		Development/C++
Obsoletes:	%{libname}-examples < %{version}-%{release}
Provides:	%{libname}-examples = %{version}-%{release}

%description -n	%{name}-examples
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains examples, installed in the
same place as the documentation.

%prep
%if %cmake_build
%setup -q -n boost-%{version}.cmake%{cmake_pl}
%else
%setup -q -n boost_%{packver}
%endif
%apply_patches

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;

%build
%if %cmake_build
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_SINGLE_THREADED=NO \
	-DINSTALL_VERSIONED=OFF -DWITH_MPI=OFF
%make

%else

%define boost_jam_common_flags %{_smp_mflags} -d2 --layout=system --toolset=gcc variant=release threading=multi optimization=speed linkflags="%{ldflags} -lpython%{py_ver}" debug-symbols=on -sHAVE_ICU=1 -sEXPAT_INCLUDE=%{_includedir} -sEXPAT_LIBPATH=%{_libdir} -sCXXFLAGS="%{optflags} -O3"
%ifnarch %arm %mips
%define boost_bjam bjam %{boost_jam_common_flags}
%else
%define boost_bjam bjam %{boost_jam_common_flags} --disable-long-double
%endif

%{boost_bjam} --prefix=%{_prefix} --libdir=%{_libdir}
%endif

%install
rm -rf %{buildroot}
%if %cmake_build
%makeinstall_std -C build
%else
%{boost_bjam} --prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} install
%endif

# (Anssi 01/2010) add compatibility symlinks:
for file in %{buildroot}%{_libdir}/*.so; do
	cp -a $file ${file%.so}-mt.so
done
for file in %{buildroot}%{_libdir}/*.a; do
	ln -s $file ${file%.a}-mt.a
done

# Kill any debug library versions that may show up un-invited.
rm -f %{buildroot}%{_libdir}/*-d.*
# Remove cmake configuration files used to build the Boost libraries
rm -f %{buildroot}%{_libdir}/Boost*.cmake 

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files -n %{libnamedevel}
%defattr(644, root,root, 755)
%{_libdir}/libboost_*.so
%{_includedir}/boost
%if %cmake_build
%{_datadir}/%{name}-%{version}/cmake/*.cmake
%endif

%files -n %{libnamedevel}-doc
%defattr(-,root,root)
%doc packagedoc/*

%files -n %{libnamestaticdevel}
%defattr(-,root,root)
%{_libdir}/libboost_*.a

%files -n %{name}-examples
%defattr(-,root,root)
%doc examples/*
