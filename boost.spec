%define cmake_pl 0

# From the version 13 of Fedora, the Boost libraries are delivered
# with sonames equal to the Boost version (e.g., 1.41.0). 
%define	libname %mklibname boost %{version}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s

Summary:	Portable C++ libraries
Name:		boost
Version:	1.41.0
Release:	%mkrel 1
License:	Boost
Group:		Development/C++
URL:		http://boost.org/
Source0:	http://sodium.resophonic.com/boost-cmake/%{version}.cmake%{cmake_pl}/boost-%{version}.cmake%{cmake_pl}.tar.gz
BuildRequires:	bzip2-devel
BuildRequires:	python-devel
BuildRequires:	zlib-devel
BuildRequires:	icu-devel
BuildRequires:	cmake
#BuildRequires:	openmpi-devel
BuildRequires:	expat-devel
BuildRequires:	doxygen
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

%package -n	%{libname}
Summary:	The shared libraries needed for running programs using Boost
Group:		System/Libraries
Provides:	libboost = %{version}-%{release}
Provides:	%{name} = %{version}-%{release}

%description -n	%{libname}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs dynamically linked against Boost.

%package -n	%{libnamedevel}
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Requires:	%{libname} = %{version}-%{release}
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
%setup -q -n boost-%{version}.cmake%{cmake_pl}

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;

%build
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_SINGLE_THREADED=YES \
	-DINSTALL_VERSIONED=OFF -DWITH_MPI=OFF
%make

%install
rm -rf %{buildroot}
%makeinstall_std -C build

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

%files -n %{libname}
%defattr(-,root,root)
%doc LICENSE_1_0.txt
%{_libdir}/libboost_*.so.%{version}

%files -n %{libnamedevel}
%defattr(644, root,root, 755)
%{_libdir}/libboost_*.so
%{_includedir}/boost
%{_datadir}/%{name}-%{version}/cmake/*.cmake

%files -n %{libnamedevel}-doc
%defattr(-,root,root)
%doc packagedoc/*

%files -n %{libnamestaticdevel}
%defattr(-,root,root)
%{_libdir}/libboost_*.a

%files -n %{name}-examples
%defattr(-,root,root)
%doc examples/*
