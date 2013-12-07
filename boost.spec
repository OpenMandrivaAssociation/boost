%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")
%define	libname %mklibname boost %{version}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s
%define coredevel %mklibname boost-core -d

# --no-undefined breaks build of CMakeified Boost.{Chrono,Locale,Timer}.
# Without --no-undefined, corresponding libraries lose their dependency on Boost.System.
# This is totally wrong, but it's rather a CMake'ification bug.
%define _disable_ld_no_undefined 1

Summary:	Portable C++ libraries
Name:		boost
Version:	1.53.0
Release:	8
License:	Boost
Group:		Development/C++
Url:		http://boost.org/
Source0:	http://download.sourceforge.net/boost/boost_%{packver}.tar.bz2

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

BuildRequires:	doxygen
BuildRequires:	xsltproc
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(icu-uc)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(zlib)

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

%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%global devname$lib2 %%mklibname -d boost_$(echo $lib | sed 's,[0-9]$,&_,')
%%package -n %%{devname$lib2}
Summary:	Development files for Boost $lib
Group:		Development/C++
Provides:	boost-$lib-devel = %EVRD
Requires:	%{libname$lib2} = %EVRD
Requires:	%{coredevel} = %EVRD
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string.
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{devname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %boostlibs; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{devname$lib2}
%{_libdir}/libboost_$lib*.so
%optional %{_includedir}/boost/$lib
%optional %{_includedir}/boost/$lib.hpp
%optional %{_includedir}/boost/${lib}_fwd.hpp
%if "$lib2" == "unit_test_framework"
%{_includedir}/boost/test
%endif
EOF
done)}

%define develonly accumulators algorithm archive asio assign bimap bind circular_buffer container coroutine dynamic_bitset exception flyweight format function functional fusion geometry integer mpi mpl msm multi_array multi_index multiprecision optional parameter phoenix preprocessor range ratio signals2 smart_ptr spirit tr1 tuple type_traits units unordered utility uuid variant xpressive

%{expand:%(for lib in %develonly; do lib2=${lib/-/_}; cat <<EOF
%%global devname$lib2 %%mklibname -d boost_$(echo $lib | sed 's,[0-9]$,&_,')
%%package -n %%{devname$lib2}
Summary:	Development files for Boost $lib
Group:		Development/C++
Provides:	boost-$lib-devel = %EVRD
Requires:	%{coredevel} = %EVRD
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string.
%{expand:%(for lib in %develonly; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{devname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %develonly; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{devname$lib2}
%optional %{_includedir}/boost/$lib
%optional %{_includedir}/boost/$lib.hpp
%optional %{_includedir}/boost/${lib}_fwd.hpp
%if "$lib" == "unordered"
%{_includedir}/boost/unordered_map.hpp
%{_includedir}/boost/unordered_set.hpp
%endif
EOF
done)}

%package -n	%{coredevel}
Summary:	Core development files needed by all or most Boost components
Group:		Development/C++

%description -n	%{coredevel}
Core development files needed by all or most Boost components

%package -n	%{libnamedevel}
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Requires:	%{expand:%(for lib in %boostlibs %develonly; do echo -n "%%{devname${lib/-/_}} = %{version}-%{release} "; done)}
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

%files -n %{coredevel}
%dir %{_includedir}/boost
%{_includedir}/boost/aligned_storage.hpp
%{_includedir}/boost/any.hpp
%{_includedir}/boost/array.hpp
%{_includedir}/boost/assert.hpp
%{_includedir}/boost/blank.hpp
%{_includedir}/boost/blank_fwd.hpp
%{_includedir}/boost/call_traits.hpp
%{_includedir}/boost/cast.hpp
%{_includedir}/boost/cerrno.hpp
%{_includedir}/boost/checked_delete.hpp
%{_includedir}/boost/compatibility
%{_includedir}/boost/compressed_pair.hpp
%{_includedir}/boost/concept
%{_includedir}/boost/concept_archetype.hpp
%{_includedir}/boost/concept_check.hpp
%{_includedir}/boost/concept_check
%{_includedir}/boost/config.hpp
%{_includedir}/boost/config
%{_includedir}/boost/crc.hpp
%{_includedir}/boost/cregex.hpp
%{_includedir}/boost/cstdint.hpp
%{_includedir}/boost/cstdlib.hpp
%{_includedir}/boost/current_function.hpp
%{_includedir}/boost/detail
%{_includedir}/boost/enable_shared_from_this.hpp
%{_includedir}/boost/exception_ptr.hpp
%{_includedir}/boost/foreach.hpp
%{_includedir}/boost/foreach_fwd.hpp
%{_includedir}/boost/function_equal.hpp
%{_includedir}/boost/function_output_iterator.hpp
%{_includedir}/boost/function_types
%{_includedir}/boost/generator_iterator.hpp
%{_includedir}/boost/get_pointer.hpp
%{_includedir}/boost/gil
%{_includedir}/boost/heap
%{_includedir}/boost/icl
%{_includedir}/boost/implicit_cast.hpp
%{_includedir}/boost/indirect_reference.hpp
%{_includedir}/boost/integer_traits.hpp
%{_includedir}/boost/interprocess
%{_includedir}/boost/intrusive
%{_includedir}/boost/intrusive_ptr.hpp
%{_includedir}/boost/io
%{_includedir}/boost/io_fwd.hpp
%{_includedir}/boost/is_placeholder.hpp
%{_includedir}/boost/iterator.hpp
%{_includedir}/boost/iterator
%{_includedir}/boost/iterator_adaptors.hpp
%{_includedir}/boost/lambda
%{_includedir}/boost/last_value.hpp
%{_includedir}/boost/lexical_cast.hpp
%{_includedir}/boost/limits.hpp
%{_includedir}/boost/local_function.hpp
%{_includedir}/boost/local_function
%{_includedir}/boost/lockfree
%{_includedir}/boost/logic
%{_includedir}/boost/make_shared.hpp
%{_includedir}/boost/mem_fn.hpp
%{_includedir}/boost/memory_order.hpp
%{_includedir}/boost/move
%{_includedir}/boost/multi_index_container.hpp
%{_includedir}/boost/multi_index_container_fwd.hpp
%{_includedir}/boost/next_prior.hpp
%{_includedir}/boost/non_type.hpp
%{_includedir}/boost/noncopyable.hpp
%{_includedir}/boost/nondet_random.hpp
%{_includedir}/boost/none.hpp
%{_includedir}/boost/none_t.hpp
%{_includedir}/boost/numeric
%{_includedir}/boost/operators.hpp
%{_includedir}/boost/pending
%{_includedir}/boost/pointee.hpp
%{_includedir}/boost/pointer_cast.hpp
%{_includedir}/boost/pointer_to_other.hpp
%{_includedir}/boost/polygon
%{_includedir}/boost/pool
%{_includedir}/boost/progress.hpp
%{_includedir}/boost/property_map
%{_includedir}/boost/property_tree
%{_includedir}/boost/proto
%{_includedir}/boost/ptr_container
%{_includedir}/boost/rational.hpp
%{_includedir}/boost/ref.hpp
%{_includedir}/boost/regex.h
%{_includedir}/boost/scope_exit.hpp
%{_includedir}/boost/scoped_array.hpp
%{_includedir}/boost/scoped_ptr.hpp
%{_includedir}/boost/shared_array.hpp
%{_includedir}/boost/shared_container_iterator.hpp
%{_includedir}/boost/shared_ptr.hpp
%{_includedir}/boost/signal.hpp
%{_includedir}/boost/statechart
%{_includedir}/boost/static_assert.hpp
%{_includedir}/boost/strong_typedef.hpp
%{_includedir}/boost/swap.hpp
%{_includedir}/boost/throw_exception.hpp
%{_includedir}/boost/token_functions.hpp
%{_includedir}/boost/token_iterator.hpp
%{_includedir}/boost/tokenizer.hpp
%{_includedir}/boost/type.hpp
%{_includedir}/boost/typeof
%{_includedir}/boost/version.hpp
%{_includedir}/boost/visit_each.hpp
%{_includedir}/boost/weak_ptr.hpp

%files -n %{libnamedevel}

%files -n %{libnamedevel}-doc
%doc packagedoc/*

%files -n %{libnamestaticdevel}
%{_libdir}/libboost_*.a

%files examples
%doc examples/*

%files build
%doc LICENSE_1_0.txt
%{_datadir}/boost-build/
