%define contentdir /var/www

Name:           mod_perl
Version:        2.0.3
Release:        17
Summary:        An embedded Perl interpreter for the Apache HTTP Server

Group:          System Environment/Daemons
License:        ASL 2.0
URL:            http://perl.apache.org/
Source0:        http://perl.apache.org/dist/mod_perl-%{version}.tar.gz
Source1:        perl.conf
Source2:        filter-requires.sh
Source3:        filter-provides.sh
Patch0:         mod_perl-2.0.2-multilib.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  perl-devel, perl(ExtUtils::Embed)
BuildRequires:  httpd-devel >= 2.2.0, httpd, gdbm-devel
BuildRequires:  apr-devel >= 1.2.0, apr-util-devel
Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       httpd-mmn = %(cat %{_includedir}/httpd/.mmn || echo missing)

%define __perl_requires %{SOURCE2}
%define __perl_provides %{SOURCE3}

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
Summary:        Files needed for building XS modules that use mod_perl
Group:          Development/Libraries
Requires:       mod_perl = %{version}-%{release}, httpd-devel

%description devel 
The mod_perl-devel package contains the files needed for building XS
modules that use mod_perl.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1

%build
CFLAGS="$RPM_OPT_FLAGS -fpic" %{__perl} Makefile.PL </dev/null \
	PREFIX=$RPM_BUILD_ROOT/usr \
	INSTALLDIRS=vendor \
	MP_APXS=%{_sbindir}/apxs \
	MP_APR_CONFIG=%{_bindir}/apr-1-config
make -C src/modules/perl %{?_smp_mflags} OPTIMIZE="$RPM_OPT_FLAGS -fpic"
make

%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/httpd/modules
make install \
    MODPERL_AP_LIBEXECDIR=$RPM_BUILD_ROOT%{_libdir}/httpd/modules \
    MODPERL_AP_INCLUDEDIR=$RPM_BUILD_ROOT%{_includedir}/httpd

# Remove the temporary files.
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name perllocal.pod -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -a -size 0 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'

# Fix permissions to avoid strip failures on non-root builds.
chmod -R u+w $RPM_BUILD_ROOT/*

# Install the config file
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/

# Move set of modules to -devel
devmods="ModPerl::Code ModPerl::BuildMM ModPerl::CScan \
          ModPerl::TestRun ModPerl::Config ModPerl::WrapXS \
          ModPerl::BuildOptions ModPerl::Manifest \
          ModPerl::MapUtil ModPerl::StructureMap \
          ModPerl::TypeMap ModPerl::FunctionMap \
          ModPerl::ParseSource ModPerl::MM \
          Apache2::Build Apache2::ParseSource Apache2::BuildConfig \
          Apache Bundle::ApacheTest"
for m in $devmods; do
   test -f $RPM_BUILD_ROOT%{_mandir}/man3/${m}.3pm &&
     echo "%{_mandir}/man3/${m}.3pm*"
   fn=${m//::/\/}
   test -f $RPM_BUILD_ROOT%{perl_vendorarch}/${fn}.pm &&
        echo %{perl_vendorarch}/${fn}.pm
   test -d $RPM_BUILD_ROOT%{perl_vendorarch}/${fn} && 
        echo %{perl_vendorarch}/${fn}
   test -d $RPM_BUILD_ROOT%{perl_vendorarch}/auto/${fn} && 
        echo %{perl_vendorarch}/auto/${fn}
done | tee devel.files | sed 's/^/%%exclude /' > exclude.files

# Completely remove Apache::Test - can be packaged separately
#rm -rf $RPM_BUILD_ROOT%{_mandir}/man3/Apache::Test*
#rm -rf $RPM_BUILD_ROOT%{perl_vendorarch}/Apache


%clean
rm -rf $RPM_BUILD_ROOT

%files -f exclude.files
%defattr(-,root,root,-)
%doc Changes LICENSE README* STATUS SVN-MOVE docs/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/*.conf
%{_bindir}/*
%{_libdir}/httpd/modules/mod_perl.so
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/Apache2/
%{perl_vendorarch}/Bundle/
%{perl_vendorarch}/APR/
%{perl_vendorarch}/ModPerl/
%{perl_vendorarch}/*.pm
%{_mandir}/man3/*.3*

%files devel -f devel.files
%defattr(-,root,root,-)
%{_includedir}/httpd/*

%changelog
* Tue Jan 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.3-17
- fix perl BR

* Mon Jan 28 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.3-16
- rebuild for new perl

* Thu Dec  6 2007 Joe Orton <jorton@redhat.com> 2.0.3-15
- rebuild for new OpenLDAP

* Wed Sep  5 2007 Joe Orton <jorton@redhat.com> 2.0.3-14
- filter perl(HTTP::Request::Common) Provide from -devel (#247250)

* Sun Sep  2 2007 Joe Orton <jorton@redhat.com> 2.0.3-13
- rebuild for fixed 32-bit APR

* Thu Aug 23 2007 Joe Orton <jorton@redhat.com> 2.0.3-12
- rebuild for expat soname bump

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 2.0.3-11
- rebuild for libdb soname bump

* Mon Aug 20 2007 Joe Orton <jorton@redhat.com> 2.0.3-10
- fix License

* Fri Apr 20 2007 Joe Orton <jorton@redhat.com> 2.0.3-8
- filter provide of perl(warnings) (#228429)

* Wed Feb 28 2007 Joe Orton <jorton@redhat.com> 2.0.3-7
- also restore Apache::Test to devel
- add BR for perl-devel

* Tue Feb 27 2007 Joe Orton <jorton@redhat.com> 2.0.3-6
- filter more Apache::Test requirements

* Mon Feb 26 2007 Joe Orton <jorton@redhat.com> 2.0.3-5
- repackage set of trimmed modules, but only in -devel

* Wed Jan 31 2007 Joe Orton <jorton@redhat.com> 2.0.3-4
- restore ModPerl::MM

* Tue Dec  5 2006 Joe Orton <jorton@redhat.com> 2.0.3-3
- trim modules even more aggressively (#197841)

* Mon Dec  4 2006 Joe Orton <jorton@redhat.com> 2.0.3-2
- update to 2.0.3
- remove droplet in buildroot from multilib patch
- drop build-related ModPerl:: modules and Apache::Test (#197841)
- spec file cleanups

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - sh: line 0: fg: no job control
- rebuild

* Thu Jun 15 2006 Joe Orton <jorton@redhat.com> 2.0.2-6
- fix multilib conflicts in -devel (#192733)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.0.2-5.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.0.2-3.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Dec  2 2005 Joe Orton <jorton@redhat.com> 2.0.2-3
- rebuild for httpd 2.2

* Wed Oct 26 2005 Joe Orton <jorton@redhat.com> 2.0.2-2
- update to 2.0.2

* Thu Oct 20 2005 Joe Orton <jorton@redhat.com> 2.0.1-2
- rebuild

* Fri Jun 17 2005 Warren Togami <wtogami@redhat.com> 2.0.1-1
- 2.0.1

* Fri May 20 2005 Warren Togami <wtogami@redhat.com> 2.0.0-3
- dep changes (#114651 jpo and ville)

* Fri May 20 2005 Joe Orton <jorton@redhat.com> 2.0.0-1
- update to 2.0.0 final

* Mon Apr 18 2005 Ville Skyttä <ville.skytta at iki.fi> - 2.0.0-0.rc5.3
- Fix sample configuration.
- Explicitly disable the test suite. (#112563)

* Mon Apr 18 2005 Joe Orton <jorton@redhat.com> 2.0.0-0.rc5.2
- fix filter-requires for new Apache2:: modules

* Sat Apr 16 2005 Warren Togami <wtogami@redhat.com> - 2.0.0-0.rc5.1
- 2.0.0-RC5

* Sun Apr 03 2005 Jose Pedro Oliveira <jpo@di.uminho.pt> - 2.0.0-0.rc4.1
- Update to 2.0.0-RC4.
- Specfile cleanup. (#153236)

* Tue Jan 18 2005 Chip Turner <cturner@redhat.com> 1.99_17-2
- rebuild for new perl

* Sat Dec 11 2004 Chip Turner <cturner@redhat.com> 1.99_17-1
- update to 1.99_17

* Fri Dec  3 2004 Chip Turner <cturner@redhat.com> 1.99_16-5
- rebuild

* Sun Oct  3 2004 Chip Turner <cturner@redhat.com> 1.99_16-3
- update filter-depends.sh for Module::Build and Data::Flow

* Sun Sep  5 2004 Chip Turner <cturner@redhat.com> 1.99_16-1
- update to 1.99_16

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Chip Turner <cturner@redhat.com> 1.99_12-2
- rebuild for update

* Fri Feb 13 2004 Chip Turner <cturner@redhat.com> 1.99_12-1
- update to 1.99_12

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb  6 2004 Joe Orton <jorton@redhat.com> 1.99_11-4
- rebuild to pick up libdb-4.2

* Wed Dec  3 2003 Chip Turner <cturner@redhat.com> 1.99_11-2
- fix the Requires: on httpd-mmn since it relied on the build box and not the build root

* Wed Dec  3 2003 Chip Turner <cturner@redhat.com> 1.99_11-1
- upgrade to 1.99_11
- remove aprinc patch, no longer necessary
- remove hash fix, no longer necessary

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

