Name:           netcdf
Version:        3.5.1
Release:        0.fdr.8
Epoch:          0
Summary:        Libraries for the Unidata network Common Data Form (NetCDF)

Group:          Applications/Engineering
License:        NetCDF
URL:            http://my.unidata.ucar.edu/content/software/netcdf/index.html
Source0:        ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-3.5.1.tar.Z
Patch0:         netcdf-mandir.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  gcc-g77


%description
NetCDF (network Common Data Form) is an interface for array-oriented
data access and a freely-distributed collection of software libraries
for C, Fortran, C++, and perl that provides an implementation of the
interface.  The NetCDF library also defines a machine-independent
format for representing scientific data. Together, the interface,
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


%prep
%setup -q
%patch0 -p1


%build
cd src
%ifarch x86_64
   mv macros.make.in OLD_macros.make.in
   cat OLD_macros.make.in | \
     sed -e 's|exec_prefix)/lib|exec_prefix)/lib64|' > macros.make.in
%endif
export CPPFLAGS="-DNDEBUG -Df2cFortran -fPIC"
export CFLAGS="$RPM_OPT_FLAGS -Df2cFortran -fPIC"
%configure
#  WARNING!
#  The parallel build was tested and it does NOT work.
#  make %{?_smp_mflags}
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_prefix}
mkdir -p $RPM_BUILD_ROOT/%{_datadir}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}
cd src
%makeinstall
rm -rf $RPM_BUILD_ROOT/%{_mandir}/man3f

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc src/COPYRIGHT src/README src/COMPATIBILITY
%{_bindir}/*
%{_libdir}/*.a
%{_includedir}/*
%{_mandir}/*/*


%changelog
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
