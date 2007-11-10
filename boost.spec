%define name	boost
%define version	1.34.1
%define release	%mkrel 2

%define packver	%(echo "%{version}" | sed -e "s/\\\./_/g")

%define	major		%{version}
%define	libname_orig	libboost
%define	libname		%mklibname boost %{major}
%define	libnamedevel	%mklibname boost -d
%define	libnamestaticdevel	%mklibname boost -d -s

Summary:	Portable C++ libraries
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	BSD-like
Group:		Development/C++
Source0:	http://umn.dl.sourceforge.net/sourceforge/boost/boost_%{packver}.tar.bz2
Patch2:		boost-use-rpm-optflags.patch
Patch3:		boost-run-tests.patch
# use version in soname with --layout=system as well
Patch4:		boost-layout-system.patch
URL:		http://boost.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	boost-jam >= 3.1
BuildRequires:	libbzip2-devel
BuildRequires:	libpython-devel
BuildRequires:	libz-devel
BuildRequires:	icu-devel

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

%package -n	%{libname}
Summary:	The shared libraries needed for running programs using Boost
Group:		System/Libraries
Provides:	%{libname_orig} = %{version}-%{release}
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
Obsoletes:      %{mklibname boost 1}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}

%description -n	%{libnamedevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains documentation, headers and
shared library symlinks needed for Boost development.

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

%package -n	 %{name}-examples
Summary:	The examples for the Boost libraries
Group:		Development/C++
Obsoletes:	%{libname}-examples < %{version}-%{release}
Provides:	%{libname}-examples = %{version}-%{release}

%description -n	 %{name}-examples
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains examples, installed in the
same place as the documentation.

%prep
%setup -q -n boost_%{packver}
%patch2 -p0
%patch3 -p0
%patch4 -p1
find -name '.cvsignore' -type f -print0 | xargs -0 -r rm -f
find -type f -print0 | xargs -0 chmod go-w
find -type f -print0 | xargs -0 file | grep -v script | cut -d: -f1 | xargs chmod 0644

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;

%build

# gcc.jam patched to optimization=speed => $RPM_OPT_FLAGS
%define boost_bjam bjam %{_smp_mflags} -d2 --layout=system --toolset=gcc variant=release threading=single,multi optimization=speed debug-symbols=on -sHAVE_ICU=1

%{boost_bjam} --prefix=%{_prefix} --libdir=%{_libdir}

%install
rm -rf %{buildroot}
%{boost_bjam} --prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} install

%multiarch_includes %{buildroot}%{_includedir}/boost/python/detail/wrap_python.hpp

%clean
rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

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
