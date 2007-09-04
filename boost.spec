%define name	boost
%define version	1.34.1
%define release	%mkrel 1

%define packver	%(echo "%{version}" | sed -e "s/\\\./_/g")
%define	py_ver	%(python -c 'import sys; print sys.version[0:3];')


## The Boost version numbers follow this algorithm from the FAQ:
#
# The scheme is x.y.z, where x is incremented only for massive
# changes, such as a reorganization of many libraries, y is
# incremented whenever a new library is added, and z is incremented
# for maintenance releases. y and z are reset to 0 if the value to the
# left changes.
#
# Leave the library major to 1. Set the SONAME to that major only. If
# Y increases but break compatibility and X (major) is not increased,
# then shame on them and add a version script to have something like
# libfoo.so.X(BOOST_1.Y) ?
#
# In ideal world, that'd should not happen assuming Y only increases
# with a library is added. This does not mean incompatible changes is
# possible either.
#
# Well, probably defining major to MAJOR.MINOR is better but
# changing too often? In any case, having the libraries SONAME set to
# MAJOR.MINOR.PATCHLEVEL is not nice, hence Patch1 to provide a way to
# override the actual DSO soname.

%define	major	%(echo "%{version}" | cut -d. -f1)
%define	minor	%(echo "%{version}" | cut -d. -f2)
%define	micro	%(echo "%{version}" | cut -d. -f3)
#define	major		1
%define	libname_orig	libboost
%define	libname		%mklibname boost %{major}
%define	libnamedevel	%mklibname boost -d
%define	libnamestaticdevel	%mklibname boost -d -s

Summary:	Portable C++ libraries
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	BSD style
Group:		Development/C++
Source0:	http://umn.dl.sourceforge.net/sourceforge/boost/boost_1_34_1.tar.bz2
Patch0:		boost-configure.patch
Patch1:		boost-gcc-soname.patch
Patch2:		boost-use-rpm-optflags.patch
Patch3:		boost-run-tests.patch
URL:		http://boost.org/
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	boost-jam >= 3.1
BuildRequires:	libbzip2-devel
BuildRequires:	libpython-devel
BuildRequires:	libz-devel

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
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
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
#if %{?_enable_debug_packages:1}%{?!_enable_debug_packages:0}
#define debug_build " debug"
#else
#define debug_build %{nil}
#endif

# Building all of the libraries.
# This builds python, thread, signals, regex, and test. We ignore test.
# It does not build graph, because that seems to not work at present.
# (misc) removed python, not used for the moment, and doesn't build
bjam -sTOOLS=gcc -sPYTHON_ROOT=%{_prefix} -sPYTHON_VERSION=%{py_ver} -sBUILD="release <threading>multi" -sDLLVERSION_TAG="%{major}"

%install
rm -rf %{buildroot}

bjam -sTOOLS=gcc -sPYTHON_ROOT=%{_prefix} -sPYTHON_VERSION=%{py_ver} -sBUILD="release <threading>multi" --prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} -sDLLVERSION_TAG="%{major}" install
#bjam -sTOOLS=gcc  -sBUILD="release <threading>multi" --prefix=%{buildroot}%{_prefix} -sDLLVERSION_TAG="%{major}" install

# fix include dir
mv %{buildroot}%{_includedir}/boost-%{major}_%{minor}_%{micro}/boost %{buildroot}%{_includedir}/
rmdir %{buildroot}%{_includedir}/boost-%{major}_%{minor}_%{micro}

# library installation messed up
#pushd %{buildroot}%{_libdir}
#for i in lib*-%{major}_%{minor}.so; do
#	rm -f ${i%%-%{major}_%{minor}.so}.so
#	rm -f $i.%{major}
#done
#
#for i in lib*-%{major}_%{minor}.a; do
#	rm -f ${i%%-%{major}_%{minor}.a}.a
#	ln -s $i ${i%%-%{major}_%{minor}.a}.a
#done
#
#/sbin/ldconfig -n .
#
#for i in lib*-%{major}_%{minor}.so; do
#	# (Abel) do this only after ldconfig
#	ln -s $i ${i%%-%{major}_%{minor}.so}.so
#done
#
#popd

#multiarch
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/boost/python/detail/wrap_python.hpp

%clean
rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%defattr(-,root,root)
%doc LICENSE_1_0.txt
%{_libdir}/libboost_*.so.*

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
