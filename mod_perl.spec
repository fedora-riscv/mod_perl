%define contentdir /var/www

Summary: An embedded Perl interpreter for the Apache Web server.
Name: mod_perl
Version: 1.99_09
Release: 10
Group: System Environment/Daemons
Source: http://perl.apache.org/dist/mod_perl-%{version}.tar.gz
Source1: perl.conf
Source2: filter-requires.sh
Source3: reap-stale-servers.sh
Source4: testlock.sh
Patch0: mod_perl-1.99_09-aprinc.patch
Patch2: mod_perl-1.99_09-hash.patch
License: GPL
URL: http://perl.apache.org/
BuildRoot: %{_tmppath}/%{name}-root
Requires: httpd >= 2.0.40, perl
BuildPrereq: httpd-devel >= 2.0.45-14, httpd, perl, gdbm-devel
BuildPrereq: apr-devel, apr-util-devel
Prereq: perl
Requires: httpd-mmn = %(cat %{_includedir}/httpd/.mmn)

%define __perl_requires %{SOURCE2}

%description
Mod_perl incorporates a Perl interpreter into the Apache web server,
so that the Apache web server can directly execute Perl code.
Mod_perl links the Perl runtime library into the Apache web server and
provides an object-oriented Perl interface for Apache's C language
API.  The end result is a quicker CGI script turnaround process, since
no external Perl interpreter has to be started.

Install mod_perl if you're installing the Apache web server and you'd
like for it to directly incorporate a Perl interpreter.

%package devel
Summary: Files needed for building XS modules that use mod_perl
Group: Development/Libraries
Requires: mod_perl = %{version}-%{release}, httpd-devel

%description devel 
The mod_perl-devel package contains the files needed for building XS
modules that use mod_perl.

%prep
%setup -q
%patch0 -p1 -b .aprinc
%patch2 -p0 -b .hash

%build
%{__perl} Makefile.PL </dev/null \
	PREFIX=$RPM_BUILD_ROOT/usr INSTALLDIRS=vendor \
	MP_APXS=%{_sbindir}/apxs MP_APR_CONFIG=%{_bindir}/apr-config \
	CCFLAGS="$RPM_OPT_FLAGS -fPIC"
make

# Run the test suite.
#  Need to make t/htdocs/perlio because it isn't expecting to be run as
#  root and will fail tests that try and write files because the server
#  will have changed it's uid.
%ifarch 1386
mkdir t/htdocs/perlio
chmod 777 t/htdocs/perlio
$RPM_SOURCE_DIR/testlock.sh acquire
$RPM_SOURCE_DIR/reap-stale-servers.sh
make test
$RPM_SOURCE_DIR/testlock.sh release
%endif

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir}/httpd/modules
make install \
    MODPERL_AP_LIBEXECDIR=$RPM_BUILD_ROOT%{_libdir}/httpd/modules \
    MODPERL_AP_INCLUDEDIR=$RPM_BUILD_ROOT%{_includedir}/httpd

# Fix permissions of solibs to avoid strip failures on non-root builds.
find $RPM_BUILD_ROOT%{_libdir} -name "*.so" | xargs chmod u+w

# Install the config file
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -m 644 $RPM_SOURCE_DIR/perl.conf \
   $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/

# Install its manual.
#mkdir -p $RPM_BUILD_ROOT%{contentdir}/manual/mod/mod_perl
#install -c -m 644 htdocs/manual/mod/mod_perl.html \
#        $RPM_BUILD_ROOT%{contentdir}/manual/mod

#make -C faq
#rm faq/pod2htm*
#install -m644 faq/*.html $RPM_BUILD_ROOT%{contentdir}/manual/mod/mod_perl/

# Remove the temporary files.
find $RPM_BUILD_ROOT%{_libdir}/perl?/vendor_perl/*/*/auto -name "*.bs" | xargs rm
rm -f $RPM_BUILD_ROOT%{_libdir}/perl?/vendor_perl/*/*/perllocal.pod
rm -f $RPM_BUILD_ROOT%{_libdir}/perl?/*/*/perllocal.pod

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc Changes INSTALL LICENSE README docs
#%{contentdir}/manual/mod/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/*.conf
%{_bindir}/*
%{_libdir}/httpd/modules/mod_perl.so
%{_libdir}/perl?/vendor_perl/*/*/auto/*
%{_libdir}/perl?/vendor_perl/*/*/Apache
%{_libdir}/perl?/vendor_perl/*/*/Bundle/*
%{_libdir}/perl?/vendor_perl/*/*/APR
%{_libdir}/perl?/vendor_perl/*/*/ModPerl
%{_libdir}/perl?/vendor_perl/*/*/*.pm
%{_mandir}/*/*.3*

%files devel
%defattr(-,root,root)
%{_includedir}/httpd/*

%changelog
* Tue Sep  9 2003 Gary Benson <gbenson@redhat.com> 1.99_09-10
- reenable test suite on i386 only.

* Mon Sep  8 2003 Gary Benson <gbenson@redhat.com> 1.99_09-9
- Apache::Status requires Apache::compat (#103891).
- add dependency on gdbm-devel (#103889).
- avoid strip failures on non-root builds (#103889).

* Fri Sep  5 2003 Gary Benson <gbenson@redhat.com> 
- remove explicit perl dependency (#103830).

* Wed Sep  3 2003 Gary Benson <gbenson@redhat.com>
- add PerlWarn and PerlTaintCheck examples to perl.conf.

* Thu Aug 28 2003 Gary Benson <gbenson@redhat.com>
- implement locking around test suite to avoid breakage when two
  architectures are built simultaneously on the same machine.
- make the stale-server killer wait until the server is truly dead,
  and move it into the lock.

* Wed Aug 27 2003 Gary Benson <gbenson@redhat.com> 1.99_09-8
- add an Apache::Status example to /etc/httpd/conf.d/perl.conf.
- kill any stale test servers before building.

* Thu Aug 21 2003 Gary Benson <gbenson@redhat.com> 1.99_09-7
- fix bad syntax in /etc/httpd/conf.d/perl.conf (#101988).

* Tue Jul 15 2003 Gary Benson <gbenson@redhat.com> 1.99_09-6
- patch to build with perl 5.8.1.
- disable test suite.
- also build on ppc64.

* Wed Jun  4 2003 Gary Benson <gbenson@redhat.com> 1.99_09-5
- also build on s390x.

* Wed Jun  4 2003 Gary Benson <gbenson@redhat.com> 1.99_09-4
- add a build time dependency upon httpd

* Fri May 23 2003 Gary Benson <gbenson@redhat.com> 1.99_09-3
- rebuild against reverted perl, and reenable test suite

* Tue May 13 2003 Joe Orton <jorton@redhat.com> 1.99_09-2
- pick up APR include directory
- disable test suite

* Mon May 12 2003 Gary Benson <gbenson@redhat.com>
- upgrade to 1.99_09

* Mon Feb 10 2003 Gary Benson <gbenson@redhat.com> 1.99_07-5
- reenable the test suite

* Tue Jan 28 2003 Gary Benson <gbenson@redhat.com> 1.99_07-4
- disable the test suite until httpd stops being broken

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 1.99_07-3
- rebuilt

* Mon Jan 06 2003 Gary Benson <gbenson@redhat.com> 1.99_07-2
- fix <IfDefine MODPERL2> support (#75194)
- update depends filtering for rpm-4.2 (#80965)

* Mon Nov 18 2002 Gary Benson <gbenson@redhat.com> 1.99_07-1
- upgrade to 1.99_07

* Wed Nov  6 2002 Gary Benson <gbenson@redhat.com> 1.99_05-4
- rebuild in new environment

* Fri Sep 27 2002 Gary Benson <gbenson@redhat.com>
- add epoch to the perl dependency (#74570)

* Tue Sep  3 2002 Gary Benson <gbenson@redhat.com> 1.99_05-3
- tweak example in /etc/httpd/conf.d/perl.conf to be more intuitive

* Mon Sep  2 2002 Joe Orton <jorton@redhat.com> 1.99_05-2
- require httpd-mmn for module ABI compatibility

* Mon Aug 22 2002 Gary Benson <gbenson@redhat.com> 1.99_05-1
- upgrade to 1.99_05

* Mon Aug 12 2002 Gary Benson <gbenson@redhat.com> 1.99_04-3
- rebuild against httpd-2.0.40

* Wed Jul 24 2002 Gary Benson <gbenson@redhat.com> 1.99_04-2
- rebuild against new perl

* Mon Jun 24 2002 Gary Benson <gbenson@redhat.com> 1.99_04-1
- upgrade to 1.99_04
- fix APR::PerlIO test breakages

* Fri Jun 14 2002 Gary Benson <gbenson@redhat.com> 1.99_03-1
- upgrade to 1.99_03
- reenable the test suite

* Fri Jun 14 2002 Gary Benson <gbenson@redhat.com>
- move /etc/httpd2 back to /etc/httpd

* Thu Jun 14 2002 Gary Benson <gbenson@redhat.com>
- the example configuration was using the old mod_perl 1.x syntax

* Wed Jun 12 2002 Gary Benson <gbenson@redhat.com> 1.99_02-3
- filter-requires was broken

* Tue Jun 11 2002 Gary Benson <gbenson@redhat.com> 1.99_02-2
- do install the Apache-Test stuff
- whiteout some dependencies
- disable the test suite again

* Mon Jun 10 2002 Gary Benson <gbenson@redhat.com> 1.99_02-1
- upgrade to 1.99_02
- reenable the test suite

* Fri Jun  7 2002 Gary Benson <gbenson@redhat.com> 1.99_01-1
- install correctly with Perl 5.8.0
- disable the test suite temporarily

* Thu May 23 2002 Gary Benson <gbenson@redhat.com>
- don't install the Apache-Test stuff
- add the config file.

* Wed May 22 2002 Gary Benson <gbenson@redhat.com>
- automate versioned perl dependency
- update to 1.99 and change paths for httpd-2.0

* Fri May 17 2002 Nalin Dahyabhai <nalin@redhat.com> 1.26-6
- rebuild in new environment

* Wed Mar 27 2002 Chip Turner <cturner@redhat.com> 1.26-5
- move to vendor_perl

* Fri Feb 22 2002 Nalin Dahyabhai <nalin@redhat.com> 1.26-4
- rebuild

* Fri Feb  8 2002 Nalin Dahyabhai <nalin@redhat.com> 1.26-3
- rebuild

* Thu Jan 31 2002 Nalin Dahyabhai <nalin@redhat.com> 1.26-2
- turn off large file support, which makes mod_perl think that server request
  structures are the wrong size (heads-up from Doug MacEachern and Chip Turner)

* Wed Jan 23 2002 Nalin Dahyabhai <nalin@redhat.com> 1.26-1
- update to 1.26

* Wed Jan 09 2002 Tim Powers <timp@redhat.com> 1.24_01-4
- automated rebuild

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com> 1.24_01-3
- Bump release + rebuild.

* Tue Feb 27 2001 Nalin Dahyabhai <nalin@redhat.com> 1.24_01-2
- don't include .bs files

* Sat Jan 20 2001 Nalin Dahyabhai <nalin@redhat.com> 1.24_01-1
- update to 1.24_01
- add URL

* Fri Nov 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild in new environment

* Fri Aug 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- patch to fix bug in Apache::ExtUtils (#17147)

* Mon Jul 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- remove backup files from docs (#14174)

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sat Jun 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- remove workarounds for broken Perl

* Mon Jun  5 2000 Nalin Dahyabhai <nalin@redhat.com>
- get rid of multiple prefixes

* Wed May 31 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.24
- remove pre- and post-install scripts and triggers

* Thu May 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- work around weird Perl version reporting problems with a suitably weird check

* Fri Apr 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify to be able to rebuild on both 5.003 and 5.6.0
- update to 1.23

* Thu Mar 30 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild with perl 5.6.0
- add perlver macro to spec file to make handling of other perl versions easier

* Thu Mar 23 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to 1.22

* Fri Mar 03 2000 Cristian Gafton <gafton@redhat.com>
- fixed the postun script to check for upgrades. doh
- add triggerpostun to fix older versions of the package

* Mon Feb 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- make perl a prereq because it's used in %post

* Fri Feb 25 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild against Apache 1.3.12 and EAPI (release 8)

* Mon Feb 21 2000 Preston Brown <pbrown@redhat.com>
- incorporate fixes from Markus Pilzecker <mp@rhein-neckar.netsurf.de>:
- Prefix: /usr
- find apxs binary and package directories automatically

* Thu Feb 17 2000 Preston Brown <pbrown@redhat.com>
- automatically enable/disable in httpd.conf in post/postun.

* Thu Feb 10 2000 Preston Brown <pbrown@redhat.com>
- fix up some strange permissions

* Sun Feb 06 2000 Preston Brown <pbrown@redhat.com>
- rebuild to pick up gzipped man pages, new descr.

* Fri Aug 27 1999 Preston Brown <pbrown@redhat.com>
- changed paths for perl 5.00503 (RHL 6.1 version)

* Fri Jul 09 1999 Preston Brown <pbrown@redhat.com>
- added -fPIC to correct functionality on SPARC
- upgrade to 1.21, removed build cruft from old buggy mod_perl days
- added extra documentation that was missing

* Fri Apr 16 1999 Preston Brown <pbrown@redhat.com>
- bump ver. # so SWS mod_perl gets auto-upgraded

* Wed Apr 07 1999 Preston Brown <pbrown@redhat.com>
- bugfix 1.19 release from Doug

* Wed Mar 24 1999 Preston Brown <pbrown@redhat.com>
- experimental patch from Doug MacEachern <dougm@pobox.com> to fix segfault
- rebuilt against apache 1.3.6

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 3)

* Wed Feb 24 1999 Preston Brown <pbrown@redhat.com>
- Injected new description and group.

* Sun Feb 07 1999 Preston Brown <pbrown@redhat.com>
- upgraded to mod_perl 1.18.

* Mon Dec 21 1998 Preston Brown <pbrown@redhat.com>
- Upgraded to mod_perl 1.16.

* Thu Sep 03 1998 Preston Brown <pbrown@redhat.com>
- disabled stacked_handlers.  They still seem busted!
- minor updates so no conflicts with either apache / secureweb
- fixed bug building on multiple architectures

* Wed Sep 02 1998 Preston Brown <pbrown@redhat.com>
- Updates for apache 1.3.x, and mod_perl 1.15

* Fri Feb 27 1998 Cristian Gafton <gafton@redhat.com>
- added a patch to compile it as a shared object for the apache/ssl (and
  future revisions of apache)

