%define packver	%(echo "%{version}" | sed -e "s/\\\./_/g")

%define	major %{version}
%define	libname_orig libboost
%define	libname %mklibname boost %{major}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s

Summary:	Portable C++ libraries
Name:		boost
Version:	1.38.0
Release:	%mkrel 1
License:	Boost
Group:		Development/C++
URL:		http://boost.org/
Source0:	http://umn.dl.sourceforge.net/sourceforge/boost/boost_%{packver}.tar.bz2
Patch2:		%{name}_1_37_0-use-rpm-optflags.patch
Patch3:		boost-run-tests.patch
# use version in soname with --layout=system as well
Patch4:		boost-layout-system.patch
# Based on: <http://svn.boost.org/trac/boost/attachment/ticket/1615/0001-date_time-gcc-4.3-fix.patch?format=raw>
#Patch5:		boost-date_time-gcc-4.3-fix.patch
# (tpg) https://svn.boost.org/trac/boost/ticket/2469
# will be fixed in next release
Patch6:		boost_1_37_0-wrong-BOOST_NO_EXCEPTIONS-define.patch
BuildRequires:	boost-jam >= 3.1
BuildRequires:	libbzip2-devel
BuildRequires:	libpython-devel
BuildRequires:	libz-devel
BuildRequires:	icu-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

%package -n %{libname}
Summary:	The shared libraries needed for running programs using Boost
Group:		System/Libraries
Provides:	%{libname_orig} = %{version}-%{release}
Provides:	%{name} = %{version}-%{release}

%description -n	%{libname}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs dynamically linked against Boost.

%package -n %{libnamedevel}
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Requires:	%{libname} = %{version}-%{release}
Obsoletes:	%{mklibname boost 1}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n	%{libnamedevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains documentation, headers and
shared library symlinks needed for Boost development.

%package -n %{libnamestaticdevel}
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

%package -n %{name}-examples
Summary:	The examples for the Boost libraries
Group:		Development/C++
Obsoletes:	%{libname}-examples < %{version}-%{release}
Provides:	%{libname}-examples = %{version}-%{release}

%description -n %{name}-examples
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains examples, installed in the
same place as the documentation.

%prep
%setup -q -n boost_%{packver}
%patch2 -p1
%patch3 -p0
%patch4 -p0
#%patch5 -p0
%patch6 -p1

find -name '.cvsignore' -type f -print0 | xargs -0 -r rm -f
find -type f -print0 | xargs -0 chmod go-w
find -type f -print0 | xargs -0 file | grep -v script | cut -d: -f1 | xargs -d"\n" chmod 0644

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;

%build
# (tpg) compile with our optflags
sed -i -e 's/OPT_FLAGS/%{optflags} -O3/g' tools/build/v2/tools/gcc.jam

# gcc.jam patched to optimization=speed => OPT_FLAGS
%define boost_bjam bjam %{_smp_mflags} -d2 --layout=system --toolset=gcc variant=release threading=single,multi optimization=speed linkflags="%{ldflags} -lpython%{py_ver}" debug-symbols=on -sHAVE_ICU=1

%{boost_bjam} --prefix=%{_prefix} --libdir=%{_libdir}

%install
rm -rf %{buildroot}
%{boost_bjam} --prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} install

%multiarch_includes %{buildroot}%{_includedir}/boost/python/detail/wrap_python.hpp

# (anssi 11/2007) The threading library was previously available, apparently
# wrongly, as libboost_thread.so. We create a compatibility symlink (Debian
# has one as well)
ln -s libboost_thread-mt.so %{buildroot}%{_libdir}/libboost_thread.so

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files -n %{libname}
%defattr(-,root,root)
%doc LICENSE_1_0.txt
%{_libdir}/libboost_*.so.%{major}

%files -n %{libnamedevel}
%defattr(-,root,root)
%doc packagedoc/*
%{_libdir}/libboost_*.so
%{_includedir}/boost
%multiarch %{multiarch_includedir}/boost

%files -n %{libnamestaticdevel}
%defattr(-,root,root)
%{_libdir}/libboost_*.a

%files -n %{name}-examples
%defattr(-,root,root)
%doc examples/*
