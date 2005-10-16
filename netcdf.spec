Name:           netcdf
Version:        3.6.0
Release:        8.p1%{?dist}
Summary:        Libraries for the Unidata network Common Data Form (NetCDF v3)

Group:          Applications/Engineering
License:        NetCDF
URL:            http://my.unidata.ucar.edu/content/software/netcdf/index.html
Source0:        ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-3.6.0-p1.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-gfortran

%package devel
Summary:        Development files for netcdf-3
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description
NetCDF-3 (network Common Data Form ver3) is an interface for
array-oriented data access and a freely-distributed collection of
software libraries for C, Fortran, C++, and perl that provides an
implementation of the interface.  The NetCDF library also defines a
machine-independent format for representing scientific data. Together,
the interface, library, and format support the creation, access, and
sharing of scientific data. The NetCDF software was developed at the
Unidata Program Center in Boulder, Colorado.

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

%description devel
This package contains the netCDF-3 header files, static libs, and man
pages.


%prep
%setup -q -n netcdf-3.6.0-p1


%build
cd src
export FC="gfortran"
export CPPFLAGS="-fPIC"
export FFLAGS="-fPIC"
%configure
#  WARNING!
#  The parallel build was tested and it does NOT work.
#  make %{?_smp_mflags}
make
mkdir lib_g77
cp libsrc/libnetcdf.a lib_g77
make clean
CPPFLAGS="-fPIC -DpgiFortran"
%configure
make
#  The below seems to work but I worry that it would lead to odd runtime
#  errors due to possible symbol collisions in the "cfortran.h" bits.  
#  The safer thing to do is to simply build and install two libraries,  
#  one for the older g77 and one for gfortran.
#    ar cru libsrc/libnetcdf.a lib_g77/libnetcdf.a
unset FC
unset CPPFLAGS
unset FFLAGS

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}/netcdf-3
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/netcdf-3
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}
cd src
%makeinstall INCDIR=${RPM_BUILD_ROOT}%{_includedir}/netcdf-3 \
  LIBDIR=${RPM_BUILD_ROOT}%{_libdir}/netcdf-3 \
  MANDIR=${RPM_BUILD_ROOT}%{_mandir}
cp lib_g77/libnetcdf.a ${RPM_BUILD_ROOT}%{_libdir}/netcdf-3/libnetcdf_g77.a
rm -rf ${RPM_BUILD_ROOT}%{_mandir}/man3f*
find ${RPM_BUILD_ROOT}%{_includedir}/netcdf-3 -type f | xargs chmod 644
find ${RPM_BUILD_ROOT}%{_libdir}/netcdf-3 -type f | xargs chmod 644
find ${RPM_BUILD_ROOT}%{_mandir} -type f | xargs chmod 644

%clean
rm -rf ${RPM_BUILD_ROOT}


%files
%defattr(-,root,root,-)
%doc src/COPYRIGHT src/README
%{_bindir}/*
%{_mandir}/man1/*

%files devel
%defattr(-,root,root,-)
%{_includedir}/netcdf-3
%{_libdir}/netcdf-3
%{_mandir}/man3/*


%changelog
* Sun Oct 16 2005 Ed Hill <ed@eh3.com> - 3.6.0-8.p1
- building the library twice (once each for g77 and gfortran) 
  fixes an annoying problem for people who need both compilers

* Fri Sep 29 2005 Ed Hill <ed@eh3.com> - 3.6.0-7.p1
- add FFLAGS="-fPIC"

* Fri Jun 13 2005 Ed Hill <ed@eh3.com> - 3.6.0-6.p1
- rebuild

* Fri Jun  3 2005 Ed Hill <ed@eh3.com> - 3.6.0-5.p1
- bump for the build system

* Mon May  9 2005 Ed Hill <ed@eh3.com> - 3.6.0-4.p1
- remove hard-coded dist/fedora macros

* Wed May  5 2005 Ed Hill <ed@eh3.com> - 3.6.0-3.p1
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
- remove unneeded %configure flags

* Wed Dec  1 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.11
- headers in /usr/include/netcdf, libs in /usr/lib/netcdf

* Mon Oct  4 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.10
- Put headers in their own directory but leave the libraries in the 
  %{_libdir} -- there are only two libs and the majority of other
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
- removed "--prefix=/usr" from %configure

* Wed Jul 14 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.1
- Remove unnecessary parts and cleanup for submission

* Wed Jul 14 2004 Ed Hill <eh3@mit.edu> - 0:3.5.1-0.fdr.0
- Initial RPM release.
