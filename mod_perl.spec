%define perlver %(rpm -q perl --queryformat '%%{version}')
%define contentdir /var/www

Summary: An embedded Perl interpreter for the Apache Web server.
Name: mod_perl
Version: 1.99_05
Release: 1
Group: System Environment/Daemons
Source: http://perl.apache.org/dist/mod_perl-%{version}.tar.gz
Source1: perl.conf
Source2: filter-requires.sh
License: GPL
URL: http://perl.apache.org/
BuildRoot: %{_tmppath}/%{name}-root
Requires: httpd >= 2.0.40, perl >= %{perlver}
BuildPrereq: httpd-devel >= 2.0.40, perl
Prereq: perl

%define __find_requires %{SOURCE2}

%description
Mod_perl incorporates a Perl interpreter into the Apache web server,
so that the Apache web server can directly execute Perl code.
Mod_perl links the Perl runtime library into the Apache web server and
provides an object-oriented Perl interface for Apache's C language
API.  The end result is a quicker CGI script turnaround process, since
no external Perl interpreter has to be started.

Install mod_perl if you're installing the Apache web server and you'd
like for it to directly incorporate a Perl interpreter.

%prep
%setup -q

%build
# Compile the module.
%{__perl} Makefile.PL </dev/null \
	PREFIX=$RPM_BUILD_ROOT/usr INSTALLDIRS=vendor \
	MP_APXS=%{_sbindir}/apxs \
	CCFLAGS="$RPM_OPT_FLAGS -fPIC"
make

# Run the test suite.
#  Need to make t/htdocs/perlio because it isn't expecting to be run as
#  root and will fail tests that try and write files because the server
#  will have changed it's uid.
mkdir t/htdocs/perlio
chmod 777 t/htdocs/perlio
make test

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libdir}/httpd/modules
make install MODPERL_AP_LIBEXECDIR=$RPM_BUILD_ROOT%{_libdir}/httpd/modules

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

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc Changes INSTALL LICENSE README docs
#%{contentdir}/manual/mod/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/*.conf
%{_libdir}/httpd/modules/mod_perl.so
%{_libdir}/perl?/vendor_perl/*/*/auto/*
%{_libdir}/perl?/vendor_perl/*/*/Apache
%{_libdir}/perl?/vendor_perl/*/*/Apache2
%{_libdir}/perl?/vendor_perl/*/*/Bundle/*
%{_libdir}/perl?/vendor_perl/*/*/APR
%{_libdir}/perl?/vendor_perl/*/*/ModPerl
%{_libdir}/perl?/vendor_perl/*/*/*.pm
%{_mandir}/*/*.3*

%changelog
* Mon Aug 22 2002 Gary Benson <gbenson@redhat.com> 1.99_05_1
- upgrade to 1.99_05

* Mon Aug 12 2002 Gary Benson <gbenson@redhat.com> 1.99_04_3
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

