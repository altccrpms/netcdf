# AltCCRPMS
%global _cc_name %{getenv:COMPILER_NAME}
%global _cc_version %{getenv:COMPILER_VERSION}
%global _cc_name_ver %{_cc_name}-%{_cc_version}
%global _mpi_name %{getenv:MPI_NAME}
%global _mpi_version %{getenv:MPI_VERSION}
%if "%{_mpi_name}" == ""
%global _with_mpi 0
%else
%global _with_mpi 1
%endif
%if 0%{?_with_mpi}
%global _mpi_name_ver %{_mpi_name}-%{_mpi_version}
%global _name_suffix -%{_cc_name}-%{_mpi_name}
%global _name_ver_suffix -%{_cc_name_ver}-%{_mpi_name_ver}
%global _prefix /opt/%{_cc_name_ver}/%{_mpi_name_ver}/%{shortname}-%{version}
%global _modulefiledir /opt/modulefiles/MPI/%{_cc_name}/%{_cc_version}/%{_mpi_name}/%{_mpi_version}/%{shortname}
%else
%global _name_suffix -%{_cc_name}
%global _name_ver_suffix -%{_cc_name_ver}
%global _prefix /opt/%{_cc_name_ver}/%{shortname}-%{version}
%global _modulefiledir /opt/modulefiles/Compiler/%{_cc_name}/%{_cc_version}/%{shortname}
%endif
%global _sysconfdir %{_prefix}/etc
%global _defaultdocdir %{_prefix}/share/doc
%global _infodir %{_prefix}/share/info
%global _mandir %{_prefix}/share/man

# Non gcc compilers don't generate build ids
%undefine _missing_build_ids_terminate_build

%global shortname netcdf

Name:           netcdf-4.4.0%{_name_ver_suffix}
Version:        4.4.1
Release:        3%{?dist}
Summary:        Libraries for the Unidata network Common Data Form

Group:          Applications/Engineering
License:        NetCDF
URL:            http://www.unidata.ucar.edu/software/netcdf/
Source0:        https://github.com/Unidata/netcdf-c/archive/v%{version}.tar.gz#/%{shortname}-%{version}.tar.gz
Source1:        netcdf.module.in
# Upstream patch to fix hashmap issue
# https://github.com/Unidata/netcdf-c/issues/282
Patch0:         netcdf-hashmap.patch

BuildRequires:  chrpath
BuildRequires:  doxygen
BuildRequires:  hdf-static
BuildRequires:  hdf5%{_name_ver_suffix}-devel%{?_isa} >= 1.8.4
BuildRequires:  gawk
BuildRequires:  libcurl-devel
BuildRequires:  m4
BuildRequires:  zlib-devel
%ifnarch s390 s390x %{mips}
BuildRequires:  valgrind
%endif
#mpiexec segfaults if ssh is not present
#https://trac.mcs.anl.gov/projects/mpich2/ticket/1576
BuildRequires:  openssh-clients

# AltCCRPMs
Provides:       %{shortname}%{_name_suffix} = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}%{?_isa} = %{version}-%{release}


%description
NetCDF (network Common Data Form) is an interface for array-oriented 
data access and a freely-distributed collection of software libraries 
for C, Fortran, C++, and perl that provides an implementation of the 
interface.  The NetCDF library also defines a machine-independent 
format for representing scientific data.  Together, the interface, 
library, and format support the creation, access, and sharing of 
scientific data. The NetCDF software was developed at the Unidata 
Program Center in Boulder, Colorado.

NetCDF data is: 

   o Self-Describing: A NetCDF file includes information about the
     data it contains.

   o Network-transparent:  A NetCDF file is represented in a form that
     can be accessed by computers with different ways of storing
     integers, characters, and floating-point numbers.

   o Direct-access:  A small subset of a large dataset may be accessed
     efficiently, without first reading through all the preceding
     data.

   o Appendable:  Data can be appended to a NetCDF dataset along one
     dimension without copying the dataset or redefining its
     structure. The structure of a NetCDF dataset can be changed,
     though this sometimes causes the dataset to be copied.

   o Sharable:  One writer and multiple readers may simultaneously
     access the same NetCDF file.


%package devel
Summary:        Development files for netcdf
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig%{?_isa}
Requires:       hdf5%{_name_ver_suffix}-devel%{?_isa}
Requires:       libcurl-devel%{?_isa}
Provides:       %{shortname}%{_name_suffix}-devel = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-devel%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-devel = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-devel%{?_isa} = %{version}-%{release}

%description devel
This package contains the netCDF C header files, shared devel libs, and 
man pages.


%package static
Summary:        Static libs for netcdf
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-static = %{version}-%{release}
Provides:       %{shortname}%{_name_suffix}-static%{?_isa} = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-static = %{version}-%{release}
Provides:       %{shortname}%{_name_ver_suffix}-static%{?_isa} = %{version}-%{release}

%description static
This package contains the netCDF C static libs.


%prep
%setup -q -n %{shortname}-c-%{version}
%patch0 -p1 -b .hashmap
m4 libsrc/ncx.m4 > libsrc/ncx.c


%build
#Do out of tree builds
%global _configure ../configure
#Common configure options
%global configure_opts \\\
           --enable-shared \\\
           --enable-netcdf-4 \\\
           --enable-dap \\\
           --enable-extra-example-tests \\\
           CPPFLAGS="-I/usr/include/hdf -I${HDF5_INCLUDE}" \\\
           LIBS="-L${HDF5_LIB} -ldf -ljpeg" \\\
           --enable-hdf4 \\\
           --disable-dap-remote-tests \\\
%{nil}
export LDFLAGS="%{__global_ldflags} -L/usr/%{_lib}/hdf"
mkdir build
pushd build
module load hdf5
ln -s ../configure .
%if !0%{?_with_mpi}
# Serial build
%configure %{configure_opts}
%else
# MPI builds
export CC=mpicc
%configure %{configure_opts} \
  --enable-parallel-tests
%endif
make %{?_smp_mflags}
module unload hdf5
popd


%install
module load hdf5
make -C build install DESTDIR=${RPM_BUILD_ROOT}
/bin/rm -f ${RPM_BUILD_ROOT}%{_libdir}/*.la
chrpath --delete ${RPM_BUILD_ROOT}/%{_bindir}/nc{copy,dump,gen,gen3}
/bin/rm -f ${RPM_BUILD_ROOT}%{_infodir}/dir
module unload hdf5

# AltCCRPMS
# Make the environment-modules file
mkdir -p %{buildroot}%{_modulefiledir}
# Since we're doing our own substitution here, use our own definitions.
sed -e 's#@PREFIX@#'%{_prefix}'#' -e 's#@LIB@#%{_lib}#' -e 's#@ARCH@#%{_arch}#' -e 's#@CC@#%{_cc_name}#' %SOURCE1 > %{buildroot}%{_modulefiledir}/%{version}


%check
# Set to 1 to fail if tests fail
fail=1
module load hdf5
make -C build check || ( cat build/*/test-suite.log && exit $fail )
module unload hdf5


%files
%doc COPYRIGHT README.md RELEASE_NOTES.md
%dir %{_prefix}
%dir %{_bindir}
%dir %{_libdir}
%dir %{_datadir}
#Fails for unknown reason
#dir %{_defaultdocdir}
%dir %{_mandir}
%dir %{_mandir}/man1
%{_modulefiledir}
%{_bindir}/nccopy
%{_bindir}/ncdump
%{_bindir}/ncgen
%{_bindir}/ncgen3
%{_libdir}/*.so.11*
%{_mandir}/man1/*

%files devel
%doc examples
%dir %{_includedir}
%dir %{_libdir}/pkgconfig
%dir %{_mandir}/man3
%{_bindir}/nc-config
%{_includedir}/netcdf.h
%{_includedir}/netcdf_meta.h
%{_includedir}/netcdf_mem.h
%if 0%{?_with_mpi}
%{_includedir}/netcdf_par.h
%endif
%{_libdir}/libnetcdf.settings
%{_libdir}/*.so
%{_libdir}/pkgconfig/netcdf.pc
%{_mandir}/man3/*

%files static
%{_libdir}/*.a


%changelog
* Fri Aug 12 2016 Michal Toman <mtoman@fedoraproject.org> - 4.4.1-3
- No valgrind on MIPS
- Enable valgrind on arm

* Thu Jul 7 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.1-2
- Add upstream patch to fix hashmap issue

* Wed Jun 29 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.1-1
- Update to 4.4.1

* Tue Jun 28 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.0-4
- Drop mpiexec hack

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.0-2
- Rebuild ncx.c to fix arm build

* Thu Jan 21 2016 Orion Poplawski <orion@cora.nwra.com> - 4.4.0-1
- Update to 4.4.0
- Add patch to fix incorrect char definitions

* Tue Dec 22 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.3.1-7.1
- Use rpm-opt-hooks for dependency handling
- Add version specific provides/requries

* Sat Nov 07 2015 Rex Dieter <rdieter@fedoraproject.org> 4.3.3.1-7
- rebuild (hdf)

* Wed Sep 16 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.3.1-6
- Rebuild for openmpi 1.10.0

* Mon Aug 10 2015 Sandro Mani <manisandro@gmail.com> - 4.3.3.1-5
- Rebuild for RPM MPI Requires Provides Change

* Wed Jul 29 2015 Karsten Hopp <karsten@redhat.com> 4.3.3.1-4
- mpich is available on ppc64 now

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun May 17 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.3.1-2
- Rebuild for hdf5 1.8.15

* Wed Mar 11 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.3.1-1
- Update to 4.3.3.1

* Fri Feb 13 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.3-1
- Update to 4.3.3

* Tue Jan 27 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.2-7
- Fix up provides/requires for mpi packages, use %%{?_isa}.

* Wed Jan 07 2015 Orion Poplawski <orion@cora.nwra.com> - 4.3.2-6
- Rebuild for hdf5 1.8.14

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Jakub Čajka <jcajka@redhat.com> - 4.3.2-4
- Enabled tests on s390
- Disabled parallel tests on s390(x) as they hang

* Mon Jun 9 2014 Orion Poplawski <orion@cora.nwra.com> - 4.3.2-3
- Rebuild for hdf5 1.8.13, add patch for support

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 23 2014 Orion Poplawski <orion@cora.nwra.com> - 4.3.2-1
- Update to 4.3.2
- Drop utf8 patch fixed upstream
- Re-enable MPI tests

* Fri Mar 7 2014 Orion Poplawski <orion@cora.nwra.com> - 4.3.1.1-3
- Strip UTF-8 character from netcdf.h for now, causes problems with
  netcdf4-python build

* Sat Feb 22 2014 Deji Akingunola <dakingun@gmail.com> - 4.3.1.1-2
- Rebuild for mpich-3.1

* Thu Feb 6 2014 Orion Poplawski <orion@cora.nwra.com> - 4.3.1.1-1
- Update to 4.3.1.1
- Add BR m4

* Fri Dec 27 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-8
- Rebuild for hdf5 1.8.12

* Thu Dec 5 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-7
- Use BR hdf-static (bug #1038280)

* Mon Nov 4 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-6
- Enable hdf4 support

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jul 20 2013 Deji Akingunola <dakingun@gmail.com> - 4.3.0-4
- Rename mpich2 sub-packages to mpich and rebuild for mpich-3.0

* Thu Jul 11 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-3
- Rebuild for openmpi 1.7.2

* Thu May 16 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-2
- Rebuild for hdf5 1.8.11

* Mon May 13 2013 Orion Poplawski <orion@cora.nwra.com> - 4.3.0-1
- Update to 4.3.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec 03 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2.1.1-3
- Rebuild for hdf5 1.8.10
- Disable make check of the mpi code, it is hanging for some reason

* Thu Nov 1 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2.1.1-2
- Rebuild for openmpi and mpich2 soname bumps
- Use new mpi module location

* Fri Aug 3 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2.1.1-1
- Update to 4.2.1.1

* Sun Jul 22 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2.1-1
- Update to 4.2.1 final

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.1-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2.1-0.1.rc1
- Update to 4.2.1 rc1
- Rebase pkgconfig patch
- Drop fflags patch, upstream now calls nf-config

* Wed Jun 13 2012 Dan Horák <dan[at]danny.cz> - 4.2-5
- temporarily disable checks on s390 (memory corruption and stuck build)

* Tue May 15 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-4
- Rebuild with hdf5 1.8.9

* Wed Mar 21 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-3
- Update to real 4.2 final

* Tue Mar 20 2012 Dan Horák <dan[at]danny.cz> - 4.2-2
- use %%{mpi_list} also in %%check

* Fri Mar 16 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-1
- Update to 4.2 final

* Wed Mar 7 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-0.4.rc2
- Ship examples with -devel

* Wed Mar 7 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-0.3.rc2
- Enable MPI builds

* Tue Mar 6 2012 Orion Poplawski <orion@cora.nwra.com> - 4.2-0.2.rc2
- Update to 4.2-rc2
- Fortran and C++ APIs are now in separate packages

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.3-5
- Rebuilt for c++ ABI breakage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Orion Poplawski <orion@cora.nwra.com> - 4.1.3-3
- Rebuild for hdf5 1.8.8, add explicit requires

* Thu Aug 11 2011 Peter Robinson <pbrobinson@fedoraproject.org> - 4.1.3-2
- Add ARM to valgrind excludes

* Tue Jun 21 2011 Orion Poplawski <orion@cora.nwra.com> - 4.1.3-1
- Update to 4.1.3
- Update pkgconfig and fflags patches
- Drop libm patch fixed upstream

* Tue May 17 2011 Orion Poplawski <orion@cora.nwra.com> - 4.1.2-2
- Rebuild for hdf5 1.8.7

* Thu Mar 31 2011 Orion Poplawski <orion@cora.nwra.com> - 4.1.2-1
- Update to 4.1.2 (soname bump)
- Add patch to add -lm to libnetcdf4

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jul 19 2010 Dan Horák <dan[at]danny.cz> - 4.1.1-4
- no valgrind on s390(x)

* Mon Apr 19 2010 Orion Poplawski <orion@cora.nwra.com> - 4.1.1-3
- Explicitly link libnetcdf.so against -lhdf5_hl -lhdf5

* Fri Apr 9 2010 Orion Poplawski <orion@cora.nwra.com> - 4.1.1-2
- Add patch to cleanup nc-config --fflags

* Thu Apr 8 2010 Orion Poplawski <orion@cora.nwra.com> - 4.1.1-1
- Update to 4.1.1

* Fri Feb 5 2010 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-1
- Update to 4.1.0 final

* Mon Feb 1 2010 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.8.2010020100
- Update snapshot, pkgconfig patch
- Re-enable make check

* Sat Dec 5 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.7.2009120100
- Leave include files in /usr/include

* Tue Dec 1 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.6.2009120100
- Update snapshot, removes SZIP defines from header

* Fri Nov 13 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.5.2009111309
- Update snapshot
- Docs are installed now

* Wed Nov 11 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.5.2009111008
- Explicitly link libnetcdf to the hdf libraries, don't link with -lcurl

* Wed Nov 11 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.4.2009111008
- Add Requires: libcurl-devel to devel package

* Wed Nov 11 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.3.2009111008
- Drop hdf4 support - too problematic with linking all required libraries

* Wed Nov 11 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.2.2009111008
- Add patch to use proper hdf4 libraries
- Add Requires: hdf-devel, hdf5-devel to devel package
- Move nc-config to devel package

* Wed Nov 11 2009 Orion Poplawski <orion@cora.nwra.com> - 4.1.0-0.1.2009111008
- Update to 4.1.0 beta 2 snapshot
- Enable: netcdf-4, dap, hdf4, ncgen4, a lot more tests

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Apr 16 2009 Orion Poplawski <orion@cora.nwra.com> - 4.0.1-1
- Update to 4.0.1
- Add pkgconfig file

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Sep  3 2008 Orion Poplawski <orion@cora.nwra.com> - 4.0.0-1
- Update to 4.0 final
- Drop netcdf-3 symlink (bug #447158)
- Update cstring patch, partially upstreamed

* Thu May 29 2008 Balint Cristian <rezso@rdsor.ro> - 4.0.0-0.6.beta2
- fix symlink to netcdf-3

* Sun May 18 2008 Patrice Dumas <pertusus@free.fr> - 4.0.0-0.5.beta2
- use %%{_fmoddir}
- don't use %%makeinstall

* Thu May 15 2008 Balint Cristian <rezso@rdsor.ro> - 4.0.0-0.4.beta2
- re-enable ppc64 since hdf5 is now present for ppc64

* Thu May  8 2008 Ed Hill <ed@eh3.com> - 4.0.0-0.3.beta2
- make package compliant with bz # 373861

* Thu May  8 2008 Ed Hill <ed@eh3.com> - 4.0.0-0.2.beta2
- ExcludeArch: ppc64 since it doesn't (for now) have hdf5

* Wed May  7 2008 Ed Hill <ed@eh3.com> - 4.0.0-0.1.beta2
- try out upstream 4.0.0-beta2

* Wed Apr  2 2008 Orion Poplawski <orion@cora.nwra.com> - 3.6.2-7
- Change patch to include <cstring>
- Remove %%{?_smp_mflags} - not parallel build safe (fortran modules)

* Wed Feb 20 2008 Ed Hill <ed@eh3.com> - 3.6.2-6
- add patch that (hopefully?) allows the GCC 4.3 build to proceed

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.6.2-5
- Autorebuild for GCC 4.3

* Sat Aug 25 2007 Ed Hill <ed@eh3.com> - 3.6.2-4
- add BR: gawk

* Sat Aug 25 2007 Ed Hill <ed@eh3.com> - 3.6.2-3
- rebuild for BuildID

* Mon May 21 2007 Orion Poplawski <orion@cora.nwra.com> - 3.6.2-2
- Run checks

* Sat Mar 17 2007 Ed Hill <ed@eh3.com> - 3.6.2-1
- 3.6.2 has a new build system supporting shared libs

* Sat Sep  2 2006 Ed Hill <ed@eh3.com> - 3.6.1-4
- switch to compat-gcc-34-g77 instead of compat-gcc-32-g77

* Sat Sep  2 2006 Ed Hill <ed@eh3.com> - 3.6.1-3
- rebuild for imminent FC-6 release

* Thu May 11 2006 Ed Hill <ed@eh3.com> - 3.6.1-2
- add missing BuildRequires for the g77 interface

* Fri Apr 21 2006 Ed Hill <ed@eh3.com> - 3.6.1-1
- update to upstream 3.6.1

* Thu Feb 16 2006 Ed Hill <ed@eh3.com> - 3.6.0-10.p1
- rebuild for new GCC

* Thu Dec 22 2005 Orion Poplawski <orion@cora.nwra.com> - 3.6.0-9.p1
- rebuild for gcc4.1

* Sun Oct 16 2005 Ed Hill <ed@eh3.com> - 3.6.0-8.p1
- building the library twice (once each for g77 and gfortran) 
  fixes an annoying problem for people who need both compilers

* Fri Sep 30 2005 Ed Hill <ed@eh3.com> - 3.6.0-7.p1
- add FFLAGS="-fPIC"

* Fri Jun 10 2005 Ed Hill <ed@eh3.com> - 3.6.0-6.p1
- rebuild

* Fri Jun  3 2005 Ed Hill <ed@eh3.com> - 3.6.0-5.p1
- bump for the build system

* Mon May  9 2005 Ed Hill <ed@eh3.com> - 3.6.0-4.p1
- remove hard-coded dist/fedora macros

* Wed May  4 2005 Ed Hill <ed@eh3.com> - 3.6.0-3.p1
- make netcdf-devel require netcdf (bug #156748)
- cleanup environment and paths

* Tue Apr  5 2005 Ed Hill <ed@eh3.com> - 0:3.6.0-2.p1
- update for gcc-gfortran
- fix file permissions

* Sat Mar  5 2005 Ed Hill <ed@eh3.com> - 0:3.6.0-1.p1
- update for 3.6.0-p1 large-files-bug fix and remove the Epoch

* Sun Dec 12 2004 Ed Hill <eh3@mit.edu> - 0:3.6.0-0.2.beta6
- fix naming scheme for pre-releases (per Michael Schwendt)

* Sat Dec 11 2004 Ed Hill <eh3@mit.edu> - 0:3.6.0beta6-0.fdr.2
- For Fortran, use only g77 (ignore gfortran, even if its installed)

* Tue Dec  7 2004 Ed Hill <eh3@mit.edu> - 0:3.6.0beta6-0.fdr.1
- remove "BuildRequires: gcc4-gfortran"

* Sat Dec  4 2004 Ed Hill <eh3@mit.edu> - 0:3.6.0beta6-0.fdr.0
- upgrade to 3.6.0beta6
- create separate devel package that does *not* depend upon 
  the non-devel package and put the headers/libs in "netcdf-3" 
  subdirs for easy co-existance with upcoming netcdf-4

* Thu Dec  2 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.12
- remove unneeded %%configure flags

* Wed Dec  1 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.11
- headers in /usr/include/netcdf, libs in /usr/lib/netcdf

* Mon Oct  4 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.10
- Put headers in their own directory but leave the libraries in the 
  %%{_libdir} -- there are only two libs and the majority of other
  "*-devel" packages follow this pattern

* Sun Oct  3 2004 Michael Schwendt <mschwendt[AT]users.sf.net> - 0:3.5.1-0.fdr.9
- add patch to install lib and headers into own tree

* Sun Aug  1 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.8
- added -fPIC so x86_64 build works with nco package

* Fri Jul 30 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.7
- fix typo in the x86_64 build and now works on x86_64

* Thu Jul 15 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.6
- fix license

* Thu Jul 15 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.5
- fix (hopefully?) x86_64 /usr/lib64 handling

* Thu Jul 15 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.4
- replace paths with macros

* Thu Jul 15 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.3
- fix spelling

* Thu Jul 15 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.2
- removed "--prefix=/usr" from %%configure

* Wed Jul 14 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.1
- Remove unnecessary parts and cleanup for submission

* Wed Jul 14 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.0
- Initial RPM release.
