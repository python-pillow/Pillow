%global py2_incdir %(python2 -c 'import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())')
%global py2_libbuilddir %(python2 -c 'import sys; import sysconfig; print("lib.{p}-{v[0]}.{v[1]}".format(p=sysconfig.get_platform(), v=sys.version_info))')

%if 0%{?fedora} || 0%{?rhel} > 7
%global with_python3 1
%global py3_incdir %(python3 -c 'import distutils.sysconfig; print(distutils.sysconfig.get_python_inc())')
%global py3_libbuilddir %(python3 -c 'import sys; import sysconfig; print("lib.{p}-{v[0]}.{v[1]}".format(p=sysconfig.get_platform(), v=sys.version_info))')
%endif

%global srcname pillow
# bootstrap building docs (pillow is required by docutils, docutils are
#  required by sphinx; pillow build-requires sphinx)
%global with_docs 1

Name:           python-%{srcname}
Version:        6.2.1
Release:        1%{?dist}
Summary:        Python image processing library

# License: see http://www.pythonware.com/products/pil/license.htm
License:        MIT
URL:            http://python-pillow.github.io/
Source0:        https://github.com/python-pillow/Pillow/archive/%{version}/Pillow-%{version}.tar.gz

BuildRequires:  freetype-devel
BuildRequires:  gcc
BuildRequires:  ghostscript
BuildRequires:  lcms2-devel
BuildRequires:  libimagequant-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libraqm-devel
BuildRequires:  libtiff-devel
BuildRequires:  libwebp-devel
BuildRequires:  openjpeg2-devel
BuildRequires:  tk-devel
BuildRequires:  zlib-devel

BuildRequires:  python2-devel
BuildRequires:  python2-numpy
BuildRequires:  python2-olefile
BuildRequires:  python2-setuptools

%if 0%{?with_python3}
BuildRequires:  python3-cffi
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
BuildRequires:  python3-olefile
BuildRequires:  python3-qt5
BuildRequires:  python3-setuptools
%if 0%{?with_docs}
BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinx_rtd_theme
%endif
BuildRequires:  python3-tkinter
%endif

# For EpsImagePlugin.py
Requires:       ghostscript

%global __provides_exclude_from ^%{python2_sitearch}/PIL/.*\\.so$
%global __provides_exclude_from ^%{python3_sitearch}/PIL/.*\\.so$

%description
Python image processing library, fork of the Python Imaging Library (PIL)

This library provides extensive file format support, an efficient
internal representation, and powerful image processing capabilities.

There are four subpackages: tk (tk interface), qt (PIL image wrapper for Qt),
devel (development) and doc (documentation).


%package -n python2-%{srcname}
Summary:        Python 2 image processing library
%{?python_provide:%python_provide python2-%{srcname}}
Provides:       python-imaging = %{version}-%{release}
Provides:       python2-imaging = %{version}-%{release}
# For MicImagePlugin.py, FpxImagePlugin.py
Requires:       python2-olefile

%description -n python2-%{srcname}
Python image processing library, fork of the Python Imaging Library (PIL)

This library provides extensive file format support, an efficient
internal representation, and powerful image processing capabilities.

There are four subpackages: tk (tk interface), qt (PIL image wrapper for Qt),
devel (development) and doc (documentation).


%package -n python2-%{srcname}-devel
Summary:        Development files for %{srcname}
Requires:       python2-devel, libjpeg-devel, zlib-devel
Requires:       python2-%{srcname}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python2-%{srcname}-devel}
Provides:       python-imaging-devel = %{version}-%{release}
Provides:       python2-imaging-devel = %{version}-%{release}

%description -n python2-%{srcname}-devel
Development files for %{srcname}.


%if 0%{?with_python3}
%package -n python3-%{srcname}
Summary:        Python 3 image processing library
%{?python_provide:%python_provide python3-%{srcname}}
Provides:       python3-imaging = %{version}-%{release}
# For MicImagePlugin.py, FpxImagePlugin.py
Requires:       python3-olefile

%description -n python3-%{srcname}
Python image processing library, fork of the Python Imaging Library (PIL)

This library provides extensive file format support, an efficient
internal representation, and powerful image processing capabilities.

There are four subpackages: tk (tk interface), qt (PIL image wrapper for Qt),
devel (development) and doc (documentation).


%package -n python3-%{srcname}-devel
Summary:        Development files for %{srcname}
Requires:       python3-devel, libjpeg-devel, zlib-devel
Requires:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}-devel}
Provides:       python3-imaging-devel = %{version}-%{release}

%description -n python3-%{srcname}-devel
Development files for %{srcname}.


%package -n python3-%{srcname}-doc
Summary:        Documentation for %{srcname}
BuildArch:      noarch
Requires:       python3-%{srcname} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}-doc}
Provides:       python3-imaging-doc = %{version}-%{release}
Obsoletes:      python2-%{srcname}-doc < 5.4.1-4

%description -n python3-%{srcname}-doc
Documentation for %{srcname}.


%package -n python3-%{srcname}-tk
Summary:        Tk interface for %{srcname}
Requires:       python3-tkinter
Requires:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}-tk}
Provides:       python3-imaging-tk = %{version}-%{release}

%description -n python3-%{srcname}-tk
Tk interface for %{name}.


%package -n python3-%{srcname}-qt
Summary:        Qt %{srcname} image wrapper
Requires:       python3-qt5
Requires:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{srcname}-qt}
Provides:       python3-imaging-qt = %{version}-%{release}

%description -n python3-%{srcname}-qt
Qt %{srcname} image wrapper.
%endif


%prep
%autosetup -p1 -n Pillow-%{version}


%build
# Build Python 2 modules
%py2_build

%if 0%{?with_python3}
# Build Python 3 modules
%py3_build

%if 0%{?with_docs}
PYTHONPATH=$PWD/build/%py3_libbuilddir make -C docs html BUILDDIR=_build_py3 SPHINXBUILD=sphinx-build-%python3_version
rm -f docs/_build_py3/html/.buildinfo
%endif
%endif


%install
# Install Python 2 modules
install -d %{buildroot}/%{py2_incdir}/Imaging
install -m 644 src/libImaging/*.h %{buildroot}/%{py2_incdir}/Imaging
%py2_install

%if 0%{?with_python3}
# Install Python 3 modules
install -d %{buildroot}/%{py3_incdir}/Imaging
install -m 644 src/libImaging/*.h %{buildroot}/%{py3_incdir}/Imaging
%py3_install
%endif


%check
# Check Python 2 modules
ln -s $PWD/Images $PWD/build/%py2_libbuilddir/Images
cp -R $PWD/Tests $PWD/build/%py2_libbuilddir/Tests
cp -R $PWD/selftest.py $PWD/build/%py2_libbuilddir/selftest.py
pushd build/%py2_libbuilddir
PYTHONPATH=$PWD %{__python2} selftest.py
popd

%if 0%{?with_python3}
# Check Python 3 modules
ln -s $PWD/Images $PWD/build/%py3_libbuilddir/Images
cp -R $PWD/Tests $PWD/build/%py3_libbuilddir/Tests
cp -R $PWD/selftest.py $PWD/build/%py3_libbuilddir/selftest.py
pushd build/%py3_libbuilddir
PYTHONPATH=$PWD %{__python3} selftest.py
popd
%endif


%files -n python2-%{srcname}
%doc README.rst CHANGES.rst
%license docs/COPYING
%{python2_sitearch}/*
# These are in subpackages
%exclude %{python2_sitearch}/PIL/_imagingtk*
%exclude %{python2_sitearch}/PIL/ImageTk*
%exclude %{python2_sitearch}/PIL/SpiderImagePlugin*
%exclude %{python2_sitearch}/PIL/ImageQt*

%files -n python2-%{srcname}-devel
%{py2_incdir}/Imaging/

%if 0%{?with_python3}
%files -n python3-%{srcname}
%doc README.rst CHANGES.rst
%license docs/COPYING
%{python3_sitearch}/*
# These are in subpackages
%exclude %{python3_sitearch}/PIL/_imagingtk*
%exclude %{python3_sitearch}/PIL/ImageTk*
%exclude %{python3_sitearch}/PIL/SpiderImagePlugin*
%exclude %{python3_sitearch}/PIL/ImageQt*
%exclude %{python3_sitearch}/PIL/__pycache__/ImageTk*
%exclude %{python3_sitearch}/PIL/__pycache__/SpiderImagePlugin*
%exclude %{python3_sitearch}/PIL/__pycache__/ImageQt*

%files -n python3-%{srcname}-devel
%{py3_incdir}/Imaging/

%files -n python3-%{srcname}-doc
%if 0%{?with_docs}
%doc docs/_build_py3/html
%endif

%files -n python3-%{srcname}-tk
%{python3_sitearch}/PIL/_imagingtk*
%{python3_sitearch}/PIL/ImageTk*
%{python3_sitearch}/PIL/SpiderImagePlugin*
%{python3_sitearch}/PIL/__pycache__/ImageTk*
%{python3_sitearch}/PIL/__pycache__/SpiderImagePlugin*

%files -n python3-%{srcname}-qt
%{python3_sitearch}/PIL/ImageQt*
%{python3_sitearch}/PIL/__pycache__/ImageQt*
%endif


%changelog
* Mon Oct 21 2019 Sandro Mani <manisandro@gmail.com> - 6.2.1-1
- Update to 6.2.1

* Mon Oct 07 2019 Petr Viktorin <pviktori@redhat.com> - 6.2.0-2
- Remove optional build dependency on python2-cffi

* Tue Oct 01 2019 Sandro Mani <manisandro@gmail.com> - 6.2.0-1
- Update to 6.2.0

* Fri Aug 16 2019 Miro Hrončok <mhroncok@redhat.com> - 6.1.0-4
- Rebuilt for Python 3.8

* Mon Aug 12 2019 Sandro Mani <manisandro@gmail.com> - 6.1.0-3
- Drop python2-pillow-qt, python2-pillow-tk

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 6.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 01 2019 Sandro Mani <manisandro@gmail.com> - 6.1.0-1
- Update to 6.1.0

* Fri May 31 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 6.0.0-2
- Fix broken Python/C interop on s390x

* Tue Apr 02 2019 Sandro Mani <manisandro@gmail.com> - 6.0.0-1
- Update to 6.0.0

* Sun Mar 10 2019 Sandro Mani <manisandro@gmail.com> - 5.4.1-4
- Drop python2-pillow-doc

* Mon Mar 04 2019 Yatin Karel <ykarel@redhat.com> - 5.4.1-3
- Fix python3 conditional

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 07 2019 Sandro Mani <manisandro@gmail.com> - 5.4.1-1
- Update to 5.4.1

* Mon Oct 01 2018 Sandro Mani <manisandro@gmail.com> - 5.3.0-1
- Update to 5.3.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 5.2.0-2
- Rebuilt for Python 3.7

* Mon Jul 02 2018 Sandro Mani <manisandro@gmail.com> - 5.2.0-1
- Update to 5.2.0

* Wed Jun 27 2018 Miro Hrončok <mhroncok@redhat.com> - 5.1.1-3
- Fix the tkinter dependency

* Sat Jun 16 2018 Miro Hrončok <mhroncok@redhat.com> - 5.1.1-2
- Rebuilt for Python 3.7

* Wed Apr 25 2018 Sandro Mani <manisandro@gmail.com> - 5.1.1-1
- Update to 5.1.1

* Thu Apr 05 2018 Sandro Mani <manisandro@gmail.com> - 5.1.0-1
- Update to 5.1.0

* Wed Mar 07 2018 Sandro Mani <manisandro@gmail.com> - 5.0.0-3
- Add missing BR: gcc

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 03 2018 Sandro Mani <manisandro@gmail.com> - 5.0.0-1
- Update to 5.0.0

* Tue Oct 03 2017 Sandro Mani <manisandro@gmail.com> - 4.3.0-1
- Update to 4.3.0

* Tue Sep 05 2017 Troy Dawson <tdawson@redhat.com> - 4.2.1-5
- Cleanup spec file conditionals

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 4.2.1-2
- Rebuild due to bug in RPM (RHBZ #1468476)

* Thu Jul 06 2017 Sandro Mani <manisandro@gmail.com> - 4.2.1-1
- Update to 4.2.1

* Sat Jul 01 2017 Sandro Mani <manisandro@gmail.com> - 4.2.0-1
- Update to 4.2.0

* Fri Apr 28 2017 Sandro Mani <manisandro@gmail.com> - 4.1.1-1
- Update to 4.1.1

* Wed Apr 05 2017 Sandro Mani <manisandro@gmail.com> - 4.1.0-1
- Update to 4.1.0

* Wed Feb 15 2017 Sandro Mani <manisandro@gmail.com> - 4.0.0-3
- Fix some __pycache__ files in wrong subpackage (#1422606)

* Wed Feb 01 2017 Sandro Mani <manisandro@gmail.com> - 4.0.0-2
- Rebuild (libwebp)

* Tue Jan 03 2017 Sandro Mani <manisandro@gmail.com> - 4.0.0-1
- Update to 4.0.0

* Mon Dec 12 2016 Miro Hrončok <mhroncok@redhat.com> - 3.4.2-3
- Enable docs build

* Mon Dec 12 2016 Miro Hrončok <mhroncok@redhat.com> - 3.4.2-2
- Rebuild for Python 3.6

* Wed Oct 19 2016 Sandro Mani <manisandro@gmail.com> - 3.4.2-1
- Update to 3.4.2

* Tue Oct 04 2016 Sandro Mani <manisandro@gmail.com> - 3.4.1-1
- Update to 3.4.1

* Mon Oct 03 2016 Sandro Mani <manisandro@gmail.com> - 3.4.0-1
- Update to 3.4.0

* Thu Aug 18 2016 Sandro Mani <manisandro@gmail.com> - 3.3.1-1
- Update  to 3.3.1

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.0-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Sat Jul 02 2016 Sandro Mani <manisandro@gmail.com> - 3.3.0-1
- Update to 3.3.0
- Modernize spec

* Fri Apr 01 2016 Sandro Mani <manisandro@gmail.com> - 3.2.0-1
- Update to 3.2.0

* Wed Feb 10 2016 Sandro Mani <manisandro@gmail.com> - 3.1.1-3
- Fix broken python3-pillow package description

* Sun Feb 07 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 3.1.1-2
- Fix provides

* Thu Feb 04 2016 Sandro Mani <manisandro@gmail.com> - 3.1.1-1
- Update to 3.1.1
- Fixes CVE-2016-0740, CVE-2016-0775

* Mon Jan 11 2016 Toshio Kuratomi <toshio@fedoraproject.org> - 3.1.0-2
- Fix executable files in doc package bringing in python 2 for the python3 doc
  packages

* Mon Jan 04 2016 Sandro Mani <manisandro@gmail.com> - 3.1.0-1
- Update to 3.1.0

* Tue Dec 29 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 3.0.0-5
- Build with docs

* Mon Dec 28 2015 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 3.0.0-4
- Rebuilt for libwebp soname bump

* Wed Oct 14 2015 Robert Kuska <rkuska@redhat.com> - 3.0.0-3
- Rebuilt for Python3.5 rebuild with docs

* Tue Oct 13 2015 Robert Kuska <rkuska@redhat.com> - 3.0.0-2
- Rebuilt for Python3.5 rebuild without docs

* Fri Oct 02 2015 Sandro Mani <manisandro@gmail.com> - 3.0.0-1
- Update to 3.0.0

* Wed Jul 29 2015 Sandro Mani <manisandro@gmail.com> - 2.9.0-2
- Fix python3-pillow-tk Requires: tkinter -> python3-tkinter (#1248085)

* Thu Jul 02 2015 Sandro Mani <manisandro@gmail.com> - 2.9.0-1
- Update to 2.9.0

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Sandro Mani <manisandro@gmail.com> - 2.8.2-1
- Update to 2.8.2

* Thu Apr 02 2015 Sandro Mani <manisandro@gmail.com> - 2.8.1-1
- Update to 2.8.1

* Wed Apr 01 2015 Sandro Mani <manisandro@gmail.com> - 2.8.0-1
- Update to 2.8.0

* Mon Jan 12 2015 Sandro Mani <manisandro@gmail.com> - 2.7.0-1
- Update to 2.7.0
- Drop sane subpackage, is in python-sane now
- Fix python3 headers directory
- Drop Obsoletes: python3-pillow on python3-pillow-qt

* Mon Oct 13 2014 Sandro Mani <manisandro@gmail.com> - 2.6.1-1
- Update to 2.6.1

* Thu Oct 02 2014 Sandro Mani <manisandro@gmail.com> - 2.6.0-1
- Update to 2.6.0

* Wed Aug 20 2014 Sandro Mani <manisandro@gmail.com> - 2.5.3-3
- Rebuilding again to resolve transient build error that caused BZ#1131723

* Tue Aug 19 2014 Stephen Gallagher <sgallagh@redhat.com> - 2.5.3-2
- Rebuilding to resolve transient build error that caused BZ#1131723

* Tue Aug 19 2014 Sandro Mani <manisandro@gmail.com> - 2.5.3-1
- Update to 2.5.3 (Fix CVE-2014-3598, a DOS in the Jpeg2KImagePlugin)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Sandro Mani <manisandro@gmail.com> - 2.5.2-1
- Update to 2.5.2 (Fix CVE-2014-3589, a DOS in the IcnsImagePlugin)

* Sat Jul 26 2014 Sandro Mani <manisandro@gmail.com> - 2.5.1-2
- Reenable jpeg2k tests on big endian arches

* Tue Jul 15 2014 Sandro Mani <manisandro@gmail.com> - 2.5.1-1
- Update to 2.5.1

* Wed Jul 02 2014 Sandro Mani <manisandro@gmail.com> - 2.5.0-1
- Update to 2.5.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Sandro Mani <manisandro@gmail.com> - 2.4.0-10
- Rebuild with docs enabled
- Update python-pillow_openjpeg-2.1.0.patch

* Tue May 27 2014 Sandro Mani <manisandro@gmail.com> - 2.4.0-9
- Rebuild against openjpeg-2.1.0

* Fri May 23 2014 Dan Horák <dan[at]danny.cz> - 2.4.0-8
- skip jpeg2k tests on big endian arches (#1100762)

* Wed May 21 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.4.0-7
- Rebuilt for https://fedoraproject.org/wiki/Changes/f21tcl86

* Tue May 13 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.4.0-6
- Set with_docs to 1 to build docs.

* Tue May 13 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.4.0-5
- Bootstrap building sphinx docs because of circular dependency with sphinx.

* Fri May  9 2014 Orion Poplawski <orion@cora.nwra.com> - 2.4.0-4
- Rebuild for Python 3.4

* Tue Apr 22 2014 Sandro Mani <manisandro@gmail.com> - 2.4.0-3
- Add patch: Have the tempfile use a suffix with a dot

* Thu Apr 17 2014 Sandro Mani <manisandro@gmail.com> - 2.4.0-2
- Enable Jpeg2000 support
- Enable webp support also on s390* archs, bug #962091 is now fixed
- Add upstream patch for ghostscript detection

* Wed Apr 02 2014 Sandro Mani <manisandro@gmail.com> - 2.4.0-1
- Update to 2.4.0

* Wed Mar 19 2014 Sandro Mani <manisandro@gmail.com> - 2.3.1-1
- Update to 2.3.1 (Fix insecure use of tempfile.mktemp (CVE-2014-1932 CVE-2014-1933))

* Thu Mar 13 2014 Jakub Dorňák <jdornak@redhat.com> - 2.3.0-5
- python-pillow does not provide python3-imaging
  (python3-pillow does)

* Tue Jan 07 2014 Sandro Mani <manisandro@gmail.com> - 2.3.0-4
- Add missing ghostscript Requires and BuildRequires

* Mon Jan 06 2014 Sandro Mani <manisandro@gmail.com> - 2.3.0-3
- Remove python-pillow_help-theme.patch, add python-sphinx-theme-better BR

* Sun Jan 05 2014 Sandro Mani <manisandro@gmail.com> - 2.3.0-2
- Rebuild with docs enabled
- Change lcms BR to lcms2

* Thu Jan 02 2014 Sandro Mani <manisandro@gmail.com> - 2.3.0-1
- Update to 2.3.0
- Build with doc disabled to break circular python-pillow -> python-sphinx -> python pillow dependency

* Wed Oct 23 2013 Sandro Mani <manisandro@gmail.com> - 2.2.1-2
- Backport fix for decoding tiffs with correct byteorder, fixes rhbz#1019656

* Wed Oct 02 2013 Sandro Mani <manisandro@gmail.com> - 2.2.1-1
- Update to 2.2.1
- Really enable webp on ppc, but leave disabled on s390

* Thu Aug 29 2013 Sandro Mani <manisandro@gmail.com> - 2.1.0-4
- Add patch to fix incorrect PyArg_ParseTuple tuple signature, fixes rhbz#962091 and rhbz#988767.
- Renable webp support on bigendian arches

* Wed Aug 28 2013 Sandro Mani <manisandro@gmail.com> - 2.1.0-3
- Add patch to fix memory corruption caused by invalid palette size, see rhbz#1001122

* Tue Jul 30 2013 Karsten Hopp <karsten@redhat.com> 2.1.0-2
- Build without webp support on ppc* archs (#988767)

* Wed Jul 03 2013 Sandro Mani <manisandro@gmail.com> - 2.1.0-1
- Update to 2.1.0
- Run tests in builddir, not installroot
- Build python3-pillow docs with python3
- python-pillow_endian.patch upstreamed

* Mon May 13 2013 Roman Rakus <rrakus@redhat.com> - 2.0.0-10
- Build without webp support on s390* archs
  Resolves: rhbz#962059

* Sat May 11 2013 Roman Rakus <rrakus@redhat.com> - 2.0.0-9.gitd1c6db8
- Conditionaly disable build of python3 parts on RHEL system

* Wed May 08 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-8.gitd1c6db8
- Add patch to fix test failure on big-endian

* Thu Apr 25 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 2.0.0-7.gitd1c6db8
- Remove Obsoletes in the python-pillow-qt subpackage. Obsoletes isn't
  appropriate since qt support didn't exist in the previous python-pillow
  package so there's no reason to drag in python-pillow-qt when updating
  python-pillow.

* Fri Apr 19 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-6.gitd1c6db8
- Update to latest git
- python-pillow_quantization.patch now upstream
- python-pillow_endianness.patch now upstream
- Add subpackage for ImageQt module, with correct dependencies
- Add PyQt4 and numpy BR (for generating docs / running tests)

* Mon Apr 08 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-5.git93a488e
- Reenable tests on bigendian, add patches for #928927

* Sun Apr 07 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-4.git93a488e
- Update to latest git
- disable tests on bigendian (PPC*, S390*) until rhbz#928927 is fixed

* Fri Mar 22 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-3.gitde210a2
- python-pillow_tempfile.patch now upstream
- Add python3-imaging provides (bug #924867)

* Fri Mar 22 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-2.git2e88848
- Update to latest git
- Remove python-pillow-disable-test.patch, gcc is now fixed
- Add python-pillow_tempfile.patch to prevent a temporary file from getting packaged

* Tue Mar 19 2013 Sandro Mani <manisandro@gmail.com> - 2.0.0-1.git2f4207c
- Update to 2.0.0 git snapshot
- Enable python3 packages
- Add libwebp-devel BR for Pillow 2.0.0

* Wed Mar 13 2013 Peter Robinson <pbrobinson@fedoraproject.org> 1.7.8-6.20130305git
- Add ARM support

* Tue Mar 12 2013 Karsten Hopp <karsten@redhat.com> 1.7.8-5.20130305git
- add s390* and ppc* to arch detection

* Tue Mar 05 2013 Sandro Mani <manisandro@gmail.com> - 1.7.8-4.20130305git7866759
- Update to latest git snapshot
- 0001-Cast-hash-table-values-to-unsigned-long.patch now upstream
- Pillow-1.7.8-selftest.patch now upstream

* Mon Feb 25 2013 Sandro Mani <manisandro@gmail.com> - 1.7.8-3.20130210gite09ff61
- Really remove -fno-strict-aliasing
- Place comment on how to retreive source just above the Source0 line

* Mon Feb 18 2013 Sandro Mani <manisandro@gmail.com> - 1.7.8-2.20130210gite09ff61
- Rebuild without -fno-strict-aliasing
- Add patch for upstream issue #52

* Sun Feb 10 2013 Sandro Mani <manisandro@gmail.com> - 1.7.8-1.20130210gite09ff61
- Initial RPM package
