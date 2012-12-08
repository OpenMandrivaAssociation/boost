%define packver %(echo "%{version}" | sed -e "s/\\\./_/g")

# From the version 13 of Fedora, the Boost libraries are delivered
# with sonames equal to the Boost version (e.g., 1.41.0). 
%define	libname %mklibname boost %{version}
%define	libnamedevel %mklibname boost -d
%define	libnamestaticdevel %mklibname boost -d -s

# --no-undefined breaks build of CMakeified Boost.{Chrono,Locale,Timer}.
# Without --no-undefined, corresponding libraries lose their dependency on Boost.System.
# This is totally wrong, but it's rather a CMake'ification bug.
%define _disable_ld_no_undefined 1

Summary:	Portable C++ libraries
Name:		boost
Version:	1.50.0
Release:	4
License:	Boost
Group:		Development/C++
URL:		http://boost.org/
Source0:	http://sourceforge.net/projects/boost/files/boost/%{version}/boost_%(echo %version |sed -e 's,\.,_,g').tar.bz2

# Upstream patch to fixes a bug when compiled using a C++11 compiler
Patch0: http://www.boost.org/patches/1_50_0/001-unordered.patch

# The patch may break c++03, and there is therefore no plan yet to include
# it upstream: https://svn.boost.org/trac/boost/ticket/4999
Patch2: boost-1.50.0-signals-erase.patch

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

BuildRequires:	bzip2-devel
BuildRequires:	python-devel
BuildRequires:	zlib-devel
BuildRequires:	icu-devel >= 49.0
#BuildRequires:	openmpi-devel
BuildRequires:	expat-devel
BuildRequires:	doxygen xsltproc

%description
Boost is a collection of free peer-reviewed portable C++ source
libraries. The emphasis is on libraries which work well with the C++
Standard Library. This package contains only the shared libraries
needed for running programs using Boost.

	
%ifarch %arm %mips
%define boostlibs date_time filesystem graph iostreams math_c99 math_c99f math_tr1 math_tr1f prg_exec_monitor program_options python regex serialization signals system thread unit_test_framework wave wserialization random chrono locale timer	
%else		
%define boostlibs date_time filesystem graph iostreams math_c99 math_c99f math_c99l math_tr1 math_tr1f math_tr1l prg_exec_monitor program_options python regex serialization signals system thread unit_test_framework wave wserialization random chrono locale timer
%endif

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
BuildArch: noarch

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
%setup -q -n boost_%{packver}
%patch0 -p0
%patch2 -p1
%patch4 -p1
%patch5 -p1
%patch7 -p2
%patch9 -p1
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
%define boost_jam_common_flags %{_smp_mflags} -d2 --layout=system --toolset=gcc variant=release threading=multi optimization=speed linkflags="%{ldflags} -lpython%{py_ver}" debug-symbols=on -sHAVE_ICU=1 -sEXPAT_INCLUDE=%{_includedir} -sEXPAT_LIBPATH=%{_libdir} -sCXXFLAGS="%{optflags} -O3" link=shared runtime-link=shared
%ifnarch %arm %mips
%define boost_bjam bjam %{boost_jam_common_flags}
%else
%define boost_bjam bjam %{boost_jam_common_flags} --disable-long-double
%endif
./bootstrap.sh --prefix=%{_prefix} --libdir=%{_libdir}
./%{boost_bjam} --prefix=%{_prefix} --libdir=%{_libdir}

%install

./%{boost_bjam} --prefix=%{buildroot}%{_prefix} --libdir=%{buildroot}%{_libdir} install

# (Anssi 01/2010) add compatibility symlinks:		
for file in %{buildroot}%{_libdir}/*.so; do
    cp -a $file ${file%.so}-mt.so
done
for file in %{buildroot}%{_libdir}/*.a; do
    ln -s $(basename $file) ${file%.a}-mt.a
done
    
# Kill any debug library versions that may show up un-invited.
rm -f %{buildroot}%{_libdir}/*-d.* %{buildroot}%{_libdir}/*-d-mt.*
# Remove cmake configuration files used to build the Boost libraries
rm -f %{buildroot}%{_libdir}/Boost*.cmake 
# Fix packaged backup files in examples
find . %buildroot -name "*.*~" |xargs rm -f


%files -n %{libnamedevel}
%{_libdir}/libboost_*.so
%{_includedir}/boost

%files -n %{libnamedevel}-doc
%defattr(-,root,root)
%doc packagedoc/*

%files -n %{libnamestaticdevel}
%defattr(-,root,root)
%{_libdir}/libboost_*.a

%files -n %{name}-examples
%defattr(-,root,root)
%doc examples/*


%changelog
* The Oct 04 2012 Alexander Kazancev <kazancas@mandriva.org> 1.50.0-2
- sync with fedora and mageia packages
- build force with python and icu
- build mt flavour

* Mon Jul 02 2012 Crispin Boylan <crisb@mandriva.org> 1.50.0-1
+ Revision: 807763
- New release

* Sat Apr 07 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1.49.0-2
+ Revision: 789742
- Rebuild for icu 49.x

* Sat Mar 31 2012 Bernhard Rosenkraenzer <bero@bero.eu> 1.49.0-1
+ Revision: 788431
- Update to 1.49.0
- Fix up rpmlint errors

* Tue Nov 29 2011 Andrey Bondrov <abondrov@mandriva.org> 1.48.0-2
+ Revision: 735431
- Add patch from upstream to fix problem with forearch in 1.48

* Mon Nov 28 2011 Crispin Boylan <crisb@mandriva.org> 1.48.0-1
+ Revision: 734884
- New release

* Tue Sep 06 2011 Leonardo Coelho <leonardoc@mandriva.org> 1.47.0-1
+ Revision: 698384
- bump new version
- add exceptions to treat boost throw_exception

  + Matthew Dawkins <mattydaw@mandriva.org>
    - fix bootlibs macro on arm/mips

* Sun Jun 05 2011 Funda Wang <fwang@mandriva.org> 1.46.1-6
+ Revision: 682806
- rebuild for new icu

* Sun May 22 2011 Oden Eriksson <oeriksson@mandriva.com> 1.46.1-5
+ Revision: 677149
- rebuild

* Sat Apr 16 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 1.46.1-4
+ Revision: 653309
- rebuild

* Tue Mar 15 2011 Funda Wang <fwang@mandriva.org> 1.46.1-3
+ Revision: 644952
- add patch from upstream to fix lightsprk build

* Mon Mar 14 2011 Funda Wang <fwang@mandriva.org> 1.46.1-2
+ Revision: 644525
- rebuild for new icu

* Sun Mar 13 2011 Funda Wang <fwang@mandriva.org> 1.46.1-1
+ Revision: 644409
- new version 1.46.1
- add cmake patch from fedora, and synced cmake build conditioned
- drop merged patch

* Tue Nov 02 2010 Crispin Boylan <crisb@mandriva.org> 1.44.0-4mdv2011.0
+ Revision: 592080
- Patch 1 to fix boost issue #4598

* Fri Oct 29 2010 Funda Wang <fwang@mandriva.org> 1.44.0-3mdv2011.0
+ Revision: 590114
- rebuild for new python

* Thu Sep 02 2010 Thierry Vignaud <tv@mandriva.org> 1.44.0-2mdv2011.0
+ Revision: 575199
- let the doc subpackage be noarch

* Sun Aug 22 2010 Emmanuel Andry <eandry@mandriva.org> 1.44.0-1mdv2011.0
+ Revision: 572035
- New version 1.44.0

* Wed Aug 04 2010 Funda Wang <fwang@mandriva.org> 1.43.0-2mdv2011.0
+ Revision: 565900
- patch1 not needed

  + Luis Medinas <lmedinas@mandriva.org>
    - Fix static-devel symlinks.

  + Matthew Dawkins <mattydaw@mandriva.org>
    - new version 1.43.0
      added random to pkgs list

* Sun Mar 21 2010 Funda Wang <fwang@mandriva.org> 1.42.0-3mdv2010.1
+ Revision: 526045
- rebuild for new icu

* Tue Feb 23 2010 Crispin Boylan <crisb@mandriva.org> 1.42.0-2mdv2010.1
+ Revision: 509861
- Add serialization patch from svn fixes crash on exit when using dlopen libs

  + Anssi Hannula <anssi@mandriva.org>
    - rebuild for new boost

* Mon Feb 08 2010 Anssi Hannula <anssi@mandriva.org> 1.42.0-1mdv2010.1
+ Revision: 501872
- new version
- conditionally bring back support for building with bjam (there is no
  cmake-enabled version of 1.42.0 available)
- drop patches applied upstream (mapnik.patch, fix-serialization.patch)
- build only multithreaded versions of the libraries
- split the libraries into their own subpackages to minimize installation
  footprint on user systems

* Thu Feb 04 2010 Jérôme Brenier <incubusss@mandriva.org> 1.41.0-3mdv2010.1
+ Revision: 501005
- add one patch to fix serialization to build easystroke (from upstream)

* Wed Feb 03 2010 Funda Wang <fwang@mandriva.org> 1.41.0-2mdv2010.1
+ Revision: 500157
- add fedora patch to satisfy mapnik build

* Wed Feb 03 2010 Funda Wang <fwang@mandriva.org> 1.41.0-1mdv2010.1
+ Revision: 499854
- BR xsltproc
- New version 1.41.0 (cmake build based)
- drop all build patches as cmake can deal with all things :D
- revert to SONAME=VERSION, keep same with Fedora :(

  + Olivier Blin <blino@mandriva.org>
    - simplify long-double check
    - fix build on ARM and MIPS, they don't really have long double (from Arnaud Patard)

* Thu Aug 20 2009 Helio Chissini de Castro <helio@mandriva.com> 1.39.0-2mdv2010.0
+ Revision: 418718
- Added patch to fix pyside compilation. This is included in boost-to-be 1.4.0 official near release

* Sat Aug 15 2009 Emmanuel Andry <eandry@mandriva.org> 1.39.0-1mdv2010.0
+ Revision: 416502
- disable BR openmpi-devel, as it's not welcome in main

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - build with graphml support
    - build with mpi support
    - fix file permissions for -devel package
    - replace patch that sets %%optflags with a new one that takes an environment
      variable in stead (P0)
    - set same ABI major as Fedora and provide compatibility symlinks for "old"
      soname fashion. This should hopefully help decrease the amount of packages
      linked against older library versions (P1)
    - sync with some fedora patches
    - new release: 1.39.1

* Mon Mar 02 2009 Emmanuel Andry <eandry@mandriva.org> 1.38.0-2mdv2009.1
+ Revision: 346986
- New version 1.38.0
- drop P5 (merged upstream)

* Fri Jan 16 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.37.0-4mdv2009.1
+ Revision: 330353
- Patch6: fix wrong BOOST_NO_EXCEPTIONS define placement (upstream bug #2469)

* Fri Dec 26 2008 Funda Wang <fwang@mandriva.org> 1.37.0-3mdv2009.1
+ Revision: 319262
- link with libpython

* Tue Dec 23 2008 Funda Wang <fwang@mandriva.org> 1.37.0-2mdv2009.1
+ Revision: 317920
- use correct license

* Sat Dec 20 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1.37.0-1mdv2009.1
+ Revision: 316499
- use _disable_ld_no_undefined 1 (lof of python stuff)
- Patch2: rediff
- don't export optflags, better to sed them in
- use %%ldflags
- update to new version 1.37.0

* Mon Aug 18 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.36.0-1mdv2009.0
+ Revision: 273337
- new release
- drop P6 (merged upstream)
- compile with -O3

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1.35.0-3mdv2009.0
+ Revision: 234634
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Thu May 29 2008 David Walluck <walluck@mandriva.org> 1.35.0-2mdv2009.0
+ Revision: 212839
- patch for gcc 4.3 serialization fix
- patch for gcc 4.3 date_time fix

* Tue May 20 2008 Oden Eriksson <oeriksson@mandriva.com> 1.35.0-1mdv2009.0
+ Revision: 209510
- 1.35.0
- rediffed the patches
- drop upstream implemented patches (CVE-2008-0171+0172 is applied)
- fix the find logig (thanks anssi)

* Tue May 20 2008 Oden Eriksson <oeriksson@mandriva.com> 1.34.1-5mdv2009.0
+ Revision: 209434
- added P5 from fedora (gcc43 patch)

* Sat Feb 09 2008 Anssi Hannula <anssi@mandriva.org> 1.34.1-4mdv2008.1
+ Revision: 164328
- fix CVE-2008-0171 and CVE-2008-0172 (P0, #37412)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Nov 30 2007 Anssi Hannula <anssi@mandriva.org> 1.34.1-3mdv2008.1
+ Revision: 114034
- provide libboost_thread.so devel symlink for compatibility

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - add more explicit provides for devel pkg

* Thu Nov 01 2007 Anssi Hannula <anssi@mandriva.org> 1.34.1-2mdv2008.1
+ Revision: 104690
- use version as major as per upstream and debian
- remove boost-configure.patch, modifies irrelevant file
- remove boost-gcc-soname.patch, did not work as intended and is now
  unnecessary
- use --layout=system to drop gcc version from soname and remove the
  need for manual include move hack
- add patch from boost ml to include version in library name with
  --layout=system (boost-layout-system.patch)
- build with libicu
- drop obsolete hacks and comments
- use proper bjam flags (build single- and multi-threaded versions,
  release variants only, parallel build)
- ensure major correctness in filelist

* Tue Sep 04 2007 David Walluck <walluck@mandriva.org> 1.34.1-1mdv2008.1
+ Revision: 78984
- 1.34.1
- new lib policy
- rename examples subpackage
- take patches from Fedora

* Fri Jul 06 2007 Adam Williamson <awilliamson@mandriva.org> 1.33.1-6mdv2008.0
+ Revision: 49245
- add patch6 (atomicity.h has moved in recent GCC)

