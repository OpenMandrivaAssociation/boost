%define libname %mklibname boost %{version}
%define libnamedevel %mklibname boost -d
%define libnamestaticdevel %mklibname boost -d -s
%define coredevel %mklibname boost-core -d

# --no-undefined breaks build of CMakeified Boost.{Chrono,Locale,Timer}.
# Without --no-undefined, corresponding libraries lose their dependency on Boost.System.
# This is totally wrong, but it's rather a CMake'ification bug.
%define _disable_ld_no_undefined 1
%define _disable_lto 1
# Doesn't work with dual python2/python3 bits
%define _python_bytecompile_build 0

%ifarch %{aarch64}
%global optflags %{optflags} -O3 -fno-strict-aliasing -I%{_includedir}/libunwind -fPIC -fno-semantic-interposition -Wl,-z,notext
%else
%global optflags %{optflags} -O3 -fno-strict-aliasing -I%{_includedir}/libunwind -fPIC -fno-semantic-interposition
%endif

# (tpg) save 50 MiB
%bcond_with docs

%define beta beta1
%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")
%ifarch %{ix86} %{arm} %{aarch64}
%bcond_with numpy
%else
%bcond_without numpy
%endif

Summary:	Portable C++ libraries
Name:		boost
Version:	1.79.0
%if %{defined beta}
Release:	0.%{beta}.1
Source0:	https://boostorg.jfrog.io/artifactory/main/beta/%{version}.%{beta}/source/boost_%{packver}_%(echo %{beta} |sed -e 's,eta,,g').tar.bz2
%else
Release:	1
Source0:	https://boostorg.jfrog.io/artifactory/main/release/%{version}/source/boost_%{packver}.tar.bz2
%endif
License:	Boost
Group:		Development/C++
Url:		http://boost.org/
Source100:	%{name}.rpmlintrc

# Add a manual page for the sole executable, namely bjam, based on the
# on-line documentation:
# http://www.boost.org/boost-build2/doc/html/bbv2/overview.html
Patch5:		boost-1.48.0-add-bjam-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=756005
# https://svn.boost.org/trac/boost/ticket/6131
Patch7:		boost-1.50.0-foreach.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=783660
# https://svn.boost.org/trac/boost/ticket/6459 fixed
Patch10:	boost-1.50.0-long-double-1.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=784654
Patch12:	boost-1.50.0-polygon.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=828856
# https://bugzilla.redhat.com/show_bug.cgi?id=828857
Patch15:	boost-1.50.0-pool.patch

Patch17:	boost-1.57.0-python-libpython_dep.patch
Patch18:	boost-1.57.0-python-abi_letters.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1190039
Patch19:	boost-1.57.0-build-optflags.patch
#Patch21:	boost-unrecognized-option.patch

# Pull in various bimap fixes
Patch24:	https://patch-diff.githubusercontent.com/raw/boostorg/bimap/pull/18.patch
Patch26:	boost-1.73-locale-empty-vector.patch

BuildRequires:	doxygen
BuildRequires:	xsltproc
BuildRequires:	pkgconfig(libunwind)
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(icu-uc) >= 60.1
BuildRequires:	pkgconfig(python3)
%if %{with numpy}
BuildRequires:	python-numpy-devel
%endif
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(bzip2)
#BuildRequires:	openmpi-devel
%if !%{with docs}
Obsoletes:	%{libnamedevel}-doc <= %{EVRD}
%endif

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

# build section Taken from the Fedora .src.rpm.
%package build
Summary:	Cross platform build system for C++ projects
Group:		Development/C++
# boost-jam used to be maintained separately. It's now part of boost-build.
# Last separately maintained (and versioned) boost-jam was 3.1.18-11
# (which outnumbers boost versioning, so let's kill any boost-jam without Epoch)
Obsoletes:	boost-jam < 1:0.0.0-0

%description build
Boost.Build is an easy way to build C++ projects, everywhere. You name
your pieces of executable and libraries and list their sources.  Boost.Build
takes care about compiling your sources with the right options,
creating static and shared libraries, making pieces of executable, and other
chores -- whether you're using GCC, MSVC, or a dozen more supported
C++ compilers -- on Windows, OSX, Linux and commercial UNIX systems.

%define boostbinlibs chrono context contract coroutine date_time filesystem graph iostreams json locale log math prg_exec_monitor program_options random regex serialization system thread timer type_erasure unit_test_framework wave wserialization atomic container nowide

# (Anssi 01/2010) dashes are converted to underscores for macros ($lib2);
# The sed script adds _ when library name ends in number.
%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%global libname$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') %{version}
%%global old69name$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') 1.69.0
%%global old70name$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') 1.70.0
%%global old71name$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') 1.71.0
%%global old72name$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') 1.72.0
%%global old73name$lib2 %%mklibname boost_$(echo $lib | sed 's,[0-9]$,&_,') 1.73.0
%%package -n %%{libname$lib2}
Summary:	Boost $lib shared library
# no one should require this, but provided anyway for maximum compatibility:
Provides:	boost = %{EVRD}
Group:		System/Libraries
Obsoletes:	%%{old69name$lib2} < %{EVRD}
Obsoletes:	%%{old70name$lib2} < %{EVRD}
Obsoletes:	%%{old71name$lib2} < %{EVRD}
Obsoletes:	%%{old72name$lib2} < %{EVRD}
Obsoletes:	%%{old73name$lib2} < %{EVRD}
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string.
%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{libname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{libname$lib2}
%%doc LICENSE_1_0.txt
%{_libdir}/libboost_$lib*.so.%(echo %{version} |cut -d. -f1)*
EOF
done)}

%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%global devname$lib2 %%mklibname -d boost_$lib
%%package -n %%{devname$lib2}
Summary:	Development files for Boost $lib
Group:		Development/C++
Provides:	boost-$lib-devel = %{EVRD}
Requires:	%{libname$lib2} = %{EVRD}
Requires:	%{coredevel} = %{EVRD}
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string.
%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{devname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %boostbinlibs; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{devname$lib2}
%optional %{_libdir}/libboost_$lib*.so
%optional %{_includedir}/boost/$lib
%optional %{_includedir}/boost/$lib.h
%optional %{_includedir}/boost/$lib.hpp
%optional %{_includedir}/boost/${lib}_fwd.hpp
%optional %{_includedir}/boost/${lib}_macro.hpp
%if "$lib2" == "unit_test_framework"
%{_includedir}/boost/test
%{_libdir}/cmake/boost_test_exec_monitor-%{version}
%endif
%optional %{_libdir}/cmake/boost_$lib-%{version}
%optional %{_libdir}/cmake/boost_${lib}_*-%{version}
EOF
done)}

# There's no difference between develonly and develonly2. Just had to split
# them up because there's a limit on how big a %%expand-ed statement
# can get.
%define develonly accumulators algorithm any archive asio assign attributes bimap bind circular_buffer compute convert describe dll dynamic_bitset exception flyweight format function functional fusion geometry hana integer lambda2 lexical_cast metaparse mpi mpl msm multi_array multi_index multiprecision optional parameter phoenix poly_collection predef preprocessor process range ratio signals2 smart_ptr spirit stacktrace stl_interfaces tr1 tti tuple type_traits units unordered utility uuid variant variant2 vmd xpressive
%define develonly2 align beast callable_traits container_hash core fiber gil hof leaf mp11 pfr qvm qvm_lite type_index sort endian coroutine2 winapi yap safe_numerics histogram outcome static_string stacktrace_basic stacktrace_addr2line stacktrace_noop

%{expand:%(for lib in %develonly; do lib2=${lib/-/_}; cat <<EOF
%%global devname$lib2 %%mklibname -d boost_$lib
%%package -n %%{devname$lib2}
Summary:	Development files for Boost $lib
Group:		Development/C++
Provides:	boost-$lib-devel = %{EVRD}
Requires:	%{coredevel} = %{EVRD}
EOF
done)}
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
%optional %{_includedir}/boost/$lib.h
%optional %{_includedir}/boost/$lib.hpp
%optional %{_includedir}/boost/${lib}_fwd.hpp
%optional %{_includedir}/boost/${lib}_macro.hpp
%if "$lib" == "unordered"
%{_includedir}/boost/unordered_map.hpp
%{_includedir}/boost/unordered_set.hpp
%endif
%optional %{_libdir}/cmake/boost_$lib-%{version}
%if "$lib" == "stacktrace_basic"
%{_libdir}/cmake/boost_stacktrace_backtrace*-%{version}
%{_libdir}/cmake/boost_stacktrace_windbg*-%{version}
%endif
EOF
done)}

%{expand:%(for lib in %develonly2; do lib2=${lib/-/_}; cat <<EOF
%%global devname$lib2 %%mklibname -d boost_$lib
%%package -n %%{devname$lib2}
Summary:	Development files for Boost $lib
Group:		Development/C++
Provides:	boost-$lib-devel = %{EVRD}
Requires:	%{coredevel} = %{EVRD}
EOF
done)}
# (Anssi 01/2010) splitted expand contents due to rpm bug failing build,
# triggered by a too long expanded string.
%{expand:%(for lib in %develonly2; do lib2=${lib/-/_}; cat <<EOF
%%description -n %%{devname$lib2}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains the shared library needed for
running programs dynamically linked against Boost $lib.
EOF
done)}
%{expand:%(for lib in %develonly2; do lib2=${lib/-/_}; cat <<EOF
%%files -n %%{devname$lib2}
%optional %{_includedir}/boost/$lib
%optional %{_includedir}/boost/$lib.h
%optional %{_includedir}/boost/$lib.hpp
%optional %{_includedir}/boost/${lib}_fwd.hpp
%optional %{_libdir}/cmake/boost_$lib-%{version}
EOF
done)}

%define pyvernum %(echo %{py_ver}|sed -e 's,\\.,,g')
%global libnamepython3 %mklibname boost_python%{pyvernum} %{version}
%global devnamepython3 %mklibname -d boost_python%{pyvernum}
%global oldlibnamepython39 %mklibname boost_python39 1.78.0
%global olddevnamepython39 %mklibname -d boost_python39
%global oldlibnamepython3 %mklibname boost_python38 1.74.0
%global olddevnamepython3 %mklibname -d boost_python38
%global olderlibnamepython3 %mklibname boost_python37 1.71.0
%global olderdevnamepython3 %mklibname -d boost_python37

%package -n %{libnamepython3}
Summary:	Boost Python 3 shared library
Group:		System/Libraries
Provides:	boost-python = %{EVRD}
Provides:	boost-python3 = %{EVRD}
Obsoletes:	%{oldlibnamepython39} < %{EVRD}
Obsoletes:	%{oldlibnamepython3} < %{EVRD}
Obsoletes:	%{olderlibnamepython3} < %{EVRD}

%description -n %{libnamepython3}
Boost Python 3 shared library.

%files -n %{libnamepython3}
%{_libdir}/libboost_python%{pyvernum}.so.%(echo %{version} |cut -d. -f1)*

%package -n %{devnamepython3}
Summary:	Development files for the Boost Python 3 library
Group:		Development/C++
Requires:	python >= 3.0
Provides:	boost-python311-devel = %{EVRD}
Provides:	boost-python3-devel = %{EVRD}
Provides:	boost-python-devel = %{EVRD}
Obsoletes:	%{olddevnamepython39} < %{EVRD}
Obsoletes:	%{olddevnamepython3} < %{EVRD}
Obsoletes:	%{olderdevnamepython3} < %{EVRD}
Requires:	%{coredevel} = %{EVRD}
Requires:	%{libnamepython3} = %{EVRD}

%description -n %{devnamepython3}
Development files for the Boost Python 3 library.

%files -n %{devnamepython3}
%{_includedir}/boost/python
%{_includedir}/boost/python.hpp
%{_libdir}/libboost_python3*.so
%{_libdir}/cmake/boost_python-%{version}

%if %{with numpy}
# Numpy's python 2.x support has been discontinued -- no more numpy27
%global libnamenumpy3 %mklibname boost_numpy%{pyvernum} %{version}
%global devnamenumpy3 %mklibname -d boost_numpy%{pyvernum}
%global oldlibnamenumpy39 %mklibname boost_numpy39 1.78.0
%global olddevnamenumpy39 %mklibname -d boost_numpy39
%global oldlibnamenumpy3 %mklibname boost_numpy38 1.74.0
%global olddevnamenumpy3 %mklibname -d boost_numpy38
%global olderlibnamenumpy3 %mklibname boost_numpy37 1.71.0
%global olderdevnamenumpy3 %mklibname -d boost_numpy37

%package -n %{libnamenumpy3}
Summary:	Boost NumPy 3 shared library
Group:		System/Libraries
Provides:	boost-numpy = %{EVRD}
Provides:	boost-numpy3 = %{EVRD}
Obsoletes:	%{oldlibnamenumpy39} < %{EVRD}
Obsoletes:	%{oldlibnamenumpy3} < %{EVRD}
Obsoletes:	%{olderlibnamenumpy3} < %{EVRD}

%description -n %{libnamenumpy3}
Boost NumPy 3 shared library.

%files -n %{libnamenumpy3}
%{_libdir}/libboost_numpy%{pyvernum}.so.%(echo %{version} |cut -d. -f1)*

%package -n %{devnamenumpy3}
Summary:	Development files for the Boost NumPy 3 library
Group:		Development/C++
Requires:	python >= 3.0
Provides:	boost-numpy39-devel = %{EVRD}
Provides:	boost-numpy3-devel = %{EVRD}
Provides:	boost-numpy-devel = %{EVRD}
Obsoletes:	%{olddevnamenumpy39} < %{EVRD}
Obsoletes:	%{olddevnamenumpy3} < %{EVRD}
Obsoletes:	%{olderdevnamenumpy3} < %{EVRD}
Requires:	%{coredevel} = %{EVRD}

%description -n %{devnamenumpy3}
Development files for the Boost NumPy 3 library.

%files -n %{devnamenumpy3}
%{_libdir}/libboost_numpy3*.so
%{_libdir}/cmake/boost_numpy-%{version}
%endif

%package -n %{coredevel}
Summary:	Core development files needed by all or most Boost components
Group:		Development/C++

%description -n %{coredevel}
Core development files needed by all or most Boost components.

%package -n %{libnamedevel}
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Requires:	%{expand:%(for lib in %boostbinlibs %develonly %develonly2; do echo -n "%%{devname${lib/-/_}} = %{version}-%{release} "; done)}
Requires:	%{devnamepython3} = %{EVRD}
Requires:	%{coredevel} = %{EVRD}
Obsoletes:	%{mklibname boost 1}-devel < %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Provides:	lib%{name}-devel = %{EVRD}

%description -n %{libnamedevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains headers and shared library
symlinks needed for Boost development.

%if %{with docs}
%package -n %{libnamedevel}-doc
Summary:	The libraries and headers needed for Boost development
Group:		Development/C++
Conflicts:	libboost-devel < 1.41.0
Conflicts:	lib64boost-devel < 1.41.0
Obsoletes:	libboost-devel-doc < 1.48.0-2
Obsoletes:	lib64boost-devel-doc < 1.48.0-2
BuildArch:	noarch

%description -n %{libnamedevel}-doc
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains documentation needed for Boost
development.
%endif

%package -n %{libnamestaticdevel}
Summary:	Static libraries for Boost development
Group:		Development/C++
Requires:	%{libnamedevel} = %{EVRD}
Obsoletes:	%{mklibname boost 1}-static-devel < %{EVRD}
Provides:	%{name}-static-devel = %{EVRD}

%description -n %{libnamestaticdevel}
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the static libraries
needed for Boost development.

%package examples
Summary:	The examples for the Boost libraries
Group:		Development/C++
#BuildArch:	noarch

%description examples
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains examples, installed in the
same place as the documentation.

%prep
%autosetup -p1 -n boost_%{packver}
# Examples etc. get copied -- so drop patch backup files
find . -name "*~" |xargs rm
%if !%{with numpy}
# Boost.Build does not allow for disabling of numpy
# extensions, thereby leading to automagic numpy
# https://github.com/boostorg/python/issues/111#issuecomment-280447482
sed -e 's/\[ unless \[ python\.numpy \] : <build>no \]/<build>no/g' -i libs/python/build/Jamfile
%endif

# Preparing the docs
mkdir packagedoc
find -type f -not -path '*packagedoc*' \( -name '*.html' -o -name '*.htm' -o -name '*.css' -o -name '*.gif' -o -name '*.jpg' -o -name '*.png' -o -name '*README*' \) -exec cp --parents {} packagedoc/ \;
find packagedoc -type d -exec chmod +rx {} \;

# Preparing the examples: All .hpp or .cpp files that are not in
# directories called test, src, or tools, as well as all files of any
# type in directories called example or examples.
mkdir examples
find libs -type f \( -name "*.?pp" ! -path "*test*" ! -path "*src*" ! -path "*tools*" -o -path "*example*" \) -exec cp --parents {} examples/ \;
find examples -type d -exec chmod +rx {} \;
# http://www.linuxfromscratch.org/blfs/view/svn/general/boost.html
# http://osdir.com/ml/blfs-dev/2014-11/msg00142.html
# this fixed needed for kdepim4 and qt-gstreamer
sed -e '1 i#ifndef Q_MOC_RUN' -e '$ a#endif' -i boost/type_traits/detail/has_binary_operator.hpp
#sed -i 's!-m64!!g' tools/build/src/tools/gcc.jam

%build
%set_build_flags

# (tpg) we use clang by default
toolset=clang

# (tpg) https://github.com/chriskohlhoff/asio/issues/860
sed -i -e "s/define BOOST_ASIO_HAS_CO_AWAIT 1/define BOOST_ASIO_HAS_CO_AWAIT 0/g" boost/asio/detail/config.hpp
sed -i -e "s/define BOOST_ASIO_HAS_STD_COROUTINE 1/define BOOST_ASIO_HAS_STD_COROUTINE 0/g" boost/asio/detail/config.hpp

cat > ./tools/build/src/user-config.jam << EOF
using $toolset : : : <compileflags>"%{optflags}" <linkflags>"%{build_ldflags}" ;
using python : %{py3_ver} : %{__python3} : %{py3_incdir} : %{_libdir} : : : ;
EOF

./bootstrap.sh --with-toolset=$toolset --with-icu --prefix=%{_prefix} --libdir=%{_libdir} --with-python=%{__python}

# And python 3...
./b2 -d+2 -q %{?_smp_mflags} --without-mpi \
	--prefix=%{_prefix} --libdir=%{_libdir} --layout=system \
	-sICU_PATH=%{_libdir} \
	linkflags="%{build_ldflags} -lstdc++ -lm" \
%ifarch %{ix86}
	instruction-set=i686 \
%endif
%ifarch znver1
	instruction-set=znver1 \
%endif
	threading=multi debug-symbols=on pch=off variant=release python=%{py3_ver}


# Taken from the Fedora .src.rpm.
echo ============================= build Boost.Build ==================
(cd tools/build/
 ./bootstrap.sh --with-toolset=$toolset)

%install
./b2 -d+2 -q %{?_smp_mflags} --without-mpi \
	--prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} \
	debug-symbols=on pch=off python=%{py3_ver} \
%ifarch %{ix86}
	instruction-set=i686 \
%endif
%ifarch znver1
	instruction-set=znver1 \
%endif
	install

echo ============================= install Boost.Build ==================
(cd tools/build/
 ./b2 --prefix=%{buildroot}%{_prefix} install
 # Fix some permissions
 chmod +x %{buildroot}%{_datadir}/boost-build/src/tools/doxproc.py
 mkdir -p %{buildroot}%{_mandir}/man1
 cp -a v2/doc/bjam.1 %{buildroot}%{_mandir}/man1/
 # Not a real file
 rm -f %{buildroot}%{_datadir}/boost-build/build/project.ann.py
 # Empty file
 rm -f %{buildroot}%{_datadir}/boost-build/tools/doxygen/windows-paths-check.hpp
 # Let's symlink instead of shipping 2 copies of the same file
 ln -sf b2 %{buildroot}%{_bindir}/bjam
)

%if !%{with numpy}
rm -rf %{buildroot}/%{_libdir}/cmake/boost_numpy-%{version}/
%endif

%files -n %{coredevel}
%dir %{_includedir}/boost
%{_includedir}/boost/aligned_storage.hpp
%{_includedir}/boost/make_default.hpp
%{_includedir}/boost/any.hpp
%{_includedir}/boost/array.hpp
%{_includedir}/boost/assert.hpp
%{_includedir}/boost/assert
%{_includedir}/boost/blank.hpp
%{_includedir}/boost/cstdfloat.hpp
%{_includedir}/boost/make_unique.hpp
%{_includedir}/boost/polymorphic_cast.hpp
%{_includedir}/boost/polymorphic_pointer_cast.hpp
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
%{_includedir}/boost/cxx11_char_types.hpp
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
%{_includedir}/boost/operators_v1.hpp
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
%{_includedir}/boost/scope_exit.hpp
%{_includedir}/boost/scoped_array.hpp
%{_includedir}/boost/scoped_ptr.hpp
%{_includedir}/boost/shared_array.hpp
%{_includedir}/boost/shared_container_iterator.hpp
%{_includedir}/boost/shared_ptr.hpp
%{_includedir}/boost/statechart
%{_includedir}/boost/static_assert.hpp
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
%{_libdir}/cmake/Boost-%{version}
%{_libdir}/cmake/BoostDetectToolset-%{version}.cmake
%{_libdir}/cmake/boost_headers-%{version}

%files -n %{libnamedevel}

%if %{with docs}
%files -n %{libnamedevel}-doc
%doc packagedoc/*
%endif

%files -n %{libnamestaticdevel}
%{_libdir}/libboost_*.a

%files examples
%doc examples/*

%files build
%doc LICENSE_1_0.txt
%{_bindir}/bjam
%{_bindir}/b2
%{_datadir}/boost-build/
%{_mandir}/man1/bjam.1*
