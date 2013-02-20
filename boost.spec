%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")
%define	libname %mklibname boost %{version}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s

# --no-undefined breaks build of CMakeified Boost.{Chrono,Locale,Timer}.
# Without --no-undefined, corresponding libraries lose their dependency on Boost.System.
# This is totally wrong, but it's rather a CMake'ification bug.
%define _disable_ld_no_undefined 1

Summary:	Portable C++ libraries
Name:		boost
Version:	1.53.0
Release:	1
License:	Boost
Group:		Development/C++
URL:		http://boost.org/
Source0:	http://download.sourceforge.net/boost/boost_%{packver}.tar.bz2
BuildRequires:	bzip2-devel
BuildRequires:	python-devel
BuildRequires:	zlib-devel
BuildRequires:	icu-devel
BuildRequires:	expat-devel
BuildRequires:	doxygen xsltproc

# https://svn.boost.org/trac/boost/ticket/6150
Patch4: boost-1.50.0-fix-non-utf8-files.patch

# Add a manual page for the sole executable, namely bjam, based on the
# on-line documentation:
# http://www.boost.org/boost-build2/doc/html/bbv2/overview.html
Patch5: boost-1.48.0-add-bjam-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=756005
# https://svn.boost.org/trac/boost/ticket/6131
Patch7: boost-1.50.0-foreach.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=781859
# The following tickets have still to be fixed by upstream.
# https://svn.boost.org/trac/boost/ticket/6406 fixed, but only in Boost-1.51.0
# https://svn.boost.org/trac/boost/ticket/6408
# https://svn.boost.org/trac/boost/ticket/6410
# https://svn.boost.org/trac/boost/ticket/6413
# https://svn.boost.org/trac/boost/ticket/6415
Patch9: boost-1.50.0-attribute.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=783660
# https://svn.boost.org/trac/boost/ticket/6459 fixed
Patch10: boost-1.50.0-long-double-1.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=784654
Patch12: boost-1.50.0-polygon.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=828856
# https://bugzilla.redhat.com/show_bug.cgi?id=828857
Patch15: boost-1.50.0-pool.patch

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

# build section Taken from the Fedora .src.rpm.
%package build
Summary: Cross platform build system for C++ projects
Group: Development/C++
Requires: boost-jam
BuildArch: noarch

%description build
Boost.Build is an easy way to build C++ projects, everywhere. You name
your pieces of executable and libraries and list their sources.  Boost.Build
takes care about compiling your sources with the right options,
creating static and shared libraries, making pieces of executable, and other
chores -- whether you're using GCC, MSVC, or a dozen more supported
C++ compilers -- on Windows, OSX, Linux and commercial UNIX systems.

%define boostlibs chrono date_time filesystem graph iostreams locale math prg_exec_monitor program_options python random regex serialization signals system thread timer unit_test_framework wave wserialization context atomic

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
# triggered by a too long expanded string.
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{libname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{libname$lib2}
%%doc LICENSE_1_0.txt
%{_libdir}/libboost_$lib*.so.%{version}
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

%package -n	%{libnamedevel}-doc
Summary:	The libraries and headers needed for Boost development
Group:	Development/C++
Conflicts:	libboost-devel < 1.41.0
Conflicts:	lib64boost-devel < 1.41.0
Obsoletes:	libboost-devel-doc < 1.48.0-2
Obsoletes:	lib64boost-devel-doc < 1.48.0-2
BuildArch:	noarch

%description -n  %{libnamedevel}-doc
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

%package 	examples
Summary:	The examples for the Boost libraries
Group:		Development/C++
BuildArch:	noarch

%description examples
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains examples, installed in the
same place as the documentation.

%prep
%setup -q -n boost_%{packver}
%patch4 -p1
%patch5 -p1
%patch7 -p2
%patch9 -p0
%patch10 -p1
%patch12 -p3
%patch15 -p0

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;

%build
%define gcc_ver %(rpm -q --queryformat="%%{VERSION}" gcc)
cat > ./tools/build/v2/user-config.jam << EOF
using gcc : %gcc_ver : gcc : <cflags>"%optflags -I%{_includedir}/python%{py_ver}" <cxxflags>"%optflags -I%{_includedir}/python%{py_ver}" <linkflags>"%ldflags" ;
using python : %py_ver : %{_bindir}/python%{py_ver} : %{_includedir}/python%{py_ver} : %{_libdir} ;
EOF
./bootstrap.sh --with-toolset=gcc --with-icu --prefix=%{_prefix} --libdir=%{_libdir}
./b2 -d+2 -q %{?_smp_mflags} --without-mpi \
	--prefix=%{_prefix} --libdir=%{_libdir} \
	linkflags="%{ldflags} -lpython%{py_ver} -lstdc++ -lm" \
	-sHAVE_ICU=1 \
	link=shared threading=multi debug-symbols=off --layout=system

# Taken from the Fedora .src.rpm.
echo ============================= build Boost.Build ==================
(cd tools/build/v2
 ./bootstrap.sh --with-toolset=gcc)

%install
./b2 -d+2 -q %{?_smp_mflags} --without-mpi \
	--prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} \
	link=shared \
	install

echo ============================= install Boost.Build ==================
(cd tools/build/v2
 ./b2 --prefix=%{buildroot}%{_prefix} install
 # Fix some permissions
 chmod -x %{buildroot}%{_datadir}/boost-build/build/alias.py
 chmod +x %{buildroot}%{_datadir}/boost-build/tools/doxproc.py
 # We don't want to distribute this
 rm -f %{buildroot}%{_bindir}/b2
 # Not a real file
 rm -f %{buildroot}%{_datadir}/boost-build/build/project.ann.py
 # Empty file
 rm -f %{buildroot}%{_datadir}/boost-build/tools/doxygen/windows-paths-check.hpp
)
rm -f %{buildroot}/%{_bindir}/bjam
rm -f %{buildroot}/%{_mandir}/man1/bjam.1*

%files -n %{libnamedevel}
%{_libdir}/libboost_*.so
%{_includedir}/boost

%files -n %{libnamedevel}-doc
%doc packagedoc/*

%files -n %{libnamestaticdevel}
%{_libdir}/libboost_*.a

%files examples
%doc examples/*

%files build
%doc LICENSE_1_0.txt
%{_datadir}/boost-build/
