%define libname %mklibname boost
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

#define beta beta1
%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")
%ifarch %{ix86} %{arm}
%bcond_with numpy
%else
%bcond_without numpy
%endif

Summary:	Portable C++ libraries
Name:		boost
Version:	1.89.0
Release:	%{?beta:0.%{beta}.}1
%if %{defined beta}
Source0:	https://archives.boost.io/release/%{version}/source/boost_%{packver}_%(echo %{beta} |sed -e 's,eta,,g').tar.bz2
%else
Source0:	https://archives.boost.io/release/%{version}/source/boost_%{packver}.tar.bz2
%endif
Source1:	binary.template
Source2:	headers.template
Source3:	global-devel.specpart
Source4:	global-devel.desc
License:	Boost
Group:		Development/C++
Url:		https://boost.org/
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
# https://bugzilla.redhat.com/show_bug.cgi?id=1190039
Patch19:	boost-1.57.0-build-optflags.patch
#Patch21:	boost-unrecognized-option.patch

# Pull in various bimap fixes
Patch24:	https://patch-diff.githubusercontent.com/raw/boostorg/bimap/pull/18.patch

BuildRequires:	which
BuildRequires:	doxygen
BuildRequires:	xsltproc
BuildRequires:	pkgconfig(libunwind)
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(icu-uc) >= 60.1
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(mariadb)
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

%define pyvernum %(echo %{py_ver}|sed -e 's,\\.,,g')
%global libnamepython3 %mklibname boost_python%{pyvernum}
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
%global libnamenumpy3 %mklibname boost_numpy%{pyvernum}
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
BuildArch:	noarch
Obsoletes:	%{mklibname -d boost_attributes} < %{EVRD}

%description -n %{coredevel}
Core development files needed by all or most Boost components.

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

%define extra_devfiles_unordered \
%{_includedir}/boost/unordered_map.hpp \
%{_includedir}/boost/unordered_set.hpp

%define extra_devfiles_unit_test_framework \
%{_includedir}/boost/test \
%{_libdir}/cmake/boost_test_exec_monitor-%{version}

%define extra_files_serialization \
%{_libdir}/libboost_wserialization.so.*

%define extra_devfiles_serialization \
%{_libdir}/libboost_wserialization.so \
%{_libdir}/cmake/boost_wserialization-%{version}

%global extra_files_stacktrace \
%{_libdir}/libboost_stacktrace_addr2line.so.* \
%{_libdir}/libboost_stacktrace_basic.so.* \
%{_libdir}/libboost_stacktrace_noop.so.*

%ifarch %{ix86} %{x86_64}
%global extra_files_stacktrace %{extra_files_stacktrace} \
%{_libdir}/libboost_stacktrace_from_exception.so.*
%endif

%global extra_devfiles_stacktrace \
%{_libdir}/libboost_stacktrace_addr2line.so \
%{_libdir}/libboost_stacktrace_basic.so \
%{_libdir}/libboost_stacktrace_noop.so \
%{_libdir}/cmake/boost_stacktrace_addr2line-%{version} \
%{_libdir}/cmake/boost_stacktrace_basic-%{version} \
%{_libdir}/cmake/boost_stacktrace_noop-%{version}

%ifarch %{ix86} %{x86_64}
%global extra_devfiles_stacktrace %{extra_devfiles_stacktrace} \
%{_libdir}/libboost_stacktrace_from_exception.so \
%{_libdir}/cmake/boost_stacktrace_from_exception-%{version}
%endif

%define extra_files_math \
%{_libdir}/libboost_math_c99.so.%{version} \
%{_libdir}/libboost_math_c99f.so.%{version} \
%{_libdir}/libboost_math_c99l.so.%{version} \
%{_libdir}/libboost_math_tr1.so.%{version} \
%{_libdir}/libboost_math_tr1f.so.%{version} \
%{_libdir}/libboost_math_tr1l.so.%{version}

%define extra_devfiles_math \
%{_libdir}/cmake/boost_math_c99-%{version} \
%{_libdir}/cmake/boost_math_c99f-%{version} \
%{_libdir}/cmake/boost_math_c99l-%{version} \
%{_libdir}/cmake/boost_math_tr1-%{version} \
%{_libdir}/cmake/boost_math_tr1f-%{version} \
%{_libdir}/cmake/boost_math_tr1l-%{version} \
%{_libdir}/libboost_math_c99.so \
%{_libdir}/libboost_math_c99f.so \
%{_libdir}/libboost_math_c99l.so \
%{_libdir}/libboost_math_tr1.so \
%{_libdir}/libboost_math_tr1f.so \
%{_libdir}/libboost_math_tr1l.so

%define extra_files_unit_test_framework \
%{_libdir}/libboost_prg_exec_monitor.so.%{version}

%define extra_devfiles_unit_test_framework \
%{_includedir}/boost/test \
%{_libdir}/libboost_prg_exec_monitor.so \
%{_libdir}/cmake/boost_prg_exec_monitor-%{version} \
%{_libdir}/cmake/boost_test_exec_monitor-%{version}

%define extra_files_log \
%{_libdir}/libboost_log_setup.so.%{version}

%define extra_devfiles_log \
%{_libdir}/libboost_log_setup.so

%define extra_devfiles_qvm \
%{_includedir}/boost/qvm_lite.hpp

%define extra_reqprov_serialization \
Obsoletes: %{mklibname boost_wserialization} < %{EVRD}

%define extra_reqprov_devserialization \
Obsoletes: %{mklibname -d boost_wserialization} < %{EVRD}

%define extra_reqprov_devqvm \
Obsoletes: %{mklibname -d boost_qvm_lite} < %{EVRD}

%define extra_reqprov_devstacktrace \
Obsoletes: %{mklibname -d boost_stacktrace_noop} < %{EVRD} \
Obsoletes: %{mklibname -d boost_stacktrace_basic} < %{EVRD} \
Obsoletes: %{mklibname -d boost_stacktrace_addr2line} < %{EVRD}

%define extra_reqprov_devunit_test_framework \
Obsoletes: %{mklibname -d boost_prg_exec_monitor} < %{EVRD}

%define extra_reqprov_devmath \
Obsoletes: %{mklibname -d boost_tr1} < %{EVRD}


%prep
%autosetup -p1 -n boost_%{packver}
# For some reason the build system likes using windres to determine
# endianness, but windres on non-x86 is broken and windres generally
# doesn't make all that much sense on a real OS...
%ifnarch %{x86_64}
sed -i -e 's,windres,windres_does_not_exist,g' tools/build/src/tools/*.jam tools/build/src/engine/build.sh
%endif

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
	--prefix=%{_prefix} --bindir=%{_bindir} --libdir=%{_libdir} --layout=system \
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
	--prefix=%{buildroot}%{_prefix} --bindir=%{buildroot}%{_bindir} --libdir=%{buildroot}%{_libdir} \
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
 ./b2 --prefix=%{buildroot}%{_prefix} --bindir=%{buildroot}%{_bindir} install
 mkdir -p %{buildroot}%{_mandir}/man1
 cp -a v2/doc/bjam.1 %{buildroot}%{_mandir}/man1/
 # Let's symlink instead of shipping 2 copies of the same file
 ln -sf b2 %{buildroot}%{_bindir}/bjam
)

%if !%{with numpy}
rm -rf %{buildroot}/%{_libdir}/cmake/boost_numpy-%{version}/
%endif

LIBPKGS=""
DEVPKGS=""
cd %{buildroot}%{_includedir}/boost
for i in *; do
	[ -d "$i" ] || continue
	[ "$i" = "test" ] && i=unit_test_framework # Libraries named differently from headers

	# Binary package...
	[ -e %{buildroot}%{_libdir}/libboost_${i}.so ] && binary=true || binary=false
	if $binary; then
		sed -e "s,@NAME@,$i,g" %{S:1} >%{specpartsdir}/$i.specpart
		EXTRAREQ="Requires: %%{lib$i} = %{EVRD}"
		NOARCH=""
		LIBPKGS="$LIBPKGS %{mklibname boost_$i}"
	elif [ "$i" = "stacktrace" -o "$i" = "math" ]; then
		# Binaries exist, but aren't named libboost_stacktrace
		sed -e "s,@NAME@,$i,g" -e '/^%%{_libdir}/d' %{S:1} >%{specpartsdir}/$i.specpart
		EXTRAREQ="Requires: %%{lib$i} = %{EVRD}"
		NOARCH=""
		LIBPKGS="$LIBPKGS %{mklibname boost_$i}"
	else
		EXTRAREQ=""
		NOARCH="BuildArch: noarch"
	fi

	# Devel package
	sed -e "s,@NAME@,$i,g;s,@EXTRAREQ@,$EXTRAREQ,;s,@NOARCH@,$NOARCH," %{S:2} >>%{specpartsdir}/$i.specpart
	for j in %{_libdir}/libboost_$i.so \
		%{_includedir}/boost/$i \
		%{_includedir}/boost/$i.h \
		%{_includedir}/boost/$i.hpp \
		%{_includedir}/boost/${i}_fwd.hpp \
		%{_includedir}/boost/${i}_macro.hpp \
		%{_libdir}/cmake/boost_${i}-%{version} \
		%{_libdir}/cmake/boost_${i}_*-%{version}; do
		if [ -e %{buildroot}${j} ]; then
			echo $j >>%{specpartsdir}/$i.specpart
		fi
	done
	DEVPKGS="$DEVPKGS %{mklibname -d boost_$i}"
done

cp %{S:3} %{specpartsdir}/global-devel.specpart

for i in $DEVPKGS; do
	echo "Requires:	$i = %{EVRD}" >>%{specpartsdir}/global-devel.specpart
done

cat %{S:4} >>%{specpartsdir}/global-devel.specpart


%files -n %{coredevel}
%dir %{_includedir}/boost
%{_includedir}/boost/aligned_storage.hpp
%{_includedir}/boost/array.hpp
%{_includedir}/boost/blank.hpp
%{_includedir}/boost/blank_fwd.hpp
%{_includedir}/boost/call_traits.hpp
%{_includedir}/boost/cast.hpp
%{_includedir}/boost/cerrno.hpp
%{_includedir}/boost/checked_delete.hpp
%{_includedir}/boost/compressed_pair.hpp
%{_includedir}/boost/concept_archetype.hpp
%{_includedir}/boost/crc.hpp
%{_includedir}/boost/cregex.hpp
%{_includedir}/boost/cstdfloat.hpp
%{_includedir}/boost/cstdint.hpp
%{_includedir}/boost/cstdlib.hpp
%{_includedir}/boost/current_function.hpp
%{_includedir}/boost/cxx11_char_types.hpp
%{_includedir}/boost/enable_shared_from_this.hpp
%{_includedir}/boost/exception_ptr.hpp
%{_includedir}/boost/foreach.hpp
%{_includedir}/boost/foreach_fwd.hpp
%{_includedir}/boost/function_equal.hpp
%{_includedir}/boost/function_output_iterator.hpp
%{_includedir}/boost/generator_iterator.hpp
%{_includedir}/boost/get_pointer.hpp
%{_includedir}/boost/implicit_cast.hpp
%{_includedir}/boost/indirect_reference.hpp
%{_includedir}/boost/integer_traits.hpp
%{_includedir}/boost/intrusive_ptr.hpp
%{_includedir}/boost/is_placeholder.hpp
%{_includedir}/boost/iterator_adaptors.hpp
%{_includedir}/boost/limits.hpp
%{_includedir}/boost/make_default.hpp
%{_includedir}/boost/make_shared.hpp
%{_includedir}/boost/make_unique.hpp
%{_includedir}/boost/mem_fn.hpp
%{_includedir}/boost/memory_order.hpp
%{_includedir}/boost/multi_index_container.hpp
%{_includedir}/boost/multi_index_container_fwd.hpp
%{_includedir}/boost/next_prior.hpp
%{_includedir}/boost/non_type.hpp
%{_includedir}/boost/noncopyable.hpp
%{_includedir}/boost/nondet_random.hpp
%{_includedir}/boost/none.hpp
%{_includedir}/boost/none_t.hpp
%{_includedir}/boost/operators.hpp
%{_includedir}/boost/operators_v1.hpp
%{_includedir}/boost/pointee.hpp
%{_includedir}/boost/pointer_cast.hpp
%{_includedir}/boost/pointer_to_other.hpp
%{_includedir}/boost/polymorphic_cast.hpp
%{_includedir}/boost/polymorphic_pointer_cast.hpp
%{_includedir}/boost/progress.hpp
%{_includedir}/boost/rational.hpp
%{_includedir}/boost/ref.hpp
%{_includedir}/boost/scope_exit.hpp
%{_includedir}/boost/scoped_array.hpp
%{_includedir}/boost/scoped_ptr.hpp
%{_includedir}/boost/shared_array.hpp
%{_includedir}/boost/shared_container_iterator.hpp
%{_includedir}/boost/shared_ptr.hpp
%{_includedir}/boost/static_assert.hpp
%{_includedir}/boost/swap.hpp
%{_includedir}/boost/throw_exception.hpp
%{_includedir}/boost/token_functions.hpp
%{_includedir}/boost/token_iterator.hpp
%{_includedir}/boost/tokenizer.hpp
%{_includedir}/boost/type.hpp
%{_includedir}/boost/version.hpp
%{_includedir}/boost/visit_each.hpp
%{_includedir}/boost/weak_ptr.hpp
%{_libdir}/cmake/Boost-%{version}
%{_libdir}/cmake/BoostDetectToolset-%{version}.cmake
%{_libdir}/cmake/boost_headers-%{version}

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
%{_mandir}/man1/bjam.1*
%{_datadir}/b2
%{_datadir}/boost_predef
