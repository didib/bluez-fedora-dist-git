Summary: Bluetooth utilities
Name: bluez
Version: 4.13
Release: 1%{?dist}
License: GPLv2+
Group: Applications/System
Source: http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.gz
Source1: bluetooth.init
Source2: bluetooth.conf
Patch1: bluez-utils-oui-usage.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: http://www.bluez.org/

BuildRequires: flex
BuildRequires: dbus-devel >= 0.90
BuildRequires: libusb-devel, glib2-devel, alsa-lib-devel
BuildRequires: gstreamer-plugins-base-devel, gstreamer-devel
BuildRequires: libsndfile-devel

ExcludeArch: s390 s390x

Obsoletes: bluez-pan < 4.0, bluez-sdp < 4.0
Requires: initscripts, bluez-libs = %{version}
Requires: dbus >= 0.60
Requires: hwdata >= 0.215
Requires: dbus-bluez-pin-helper
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(post): /sbin/chkconfig, /sbin/service

Obsoletes: bluez-utils < 4.5-2
Provides: bluez-utils = %{version}-%{release}

%description
Utilities for use in Bluetooth applications:
	- hcitool
	- hciattach
	- hciconfig
	- bluetoothd
	- l2ping
	- start scripts (Red Hat)
	- pcmcia configuration files

The BLUETOOTH trademarks are owned by Bluetooth SIG, Inc., U.S.A.

%package libs
Summary: Libraries for use in Bluetooth applications
Group: System Environment/Libraries

%package libs-devel
Summary: Development libraries for Bluetooth applications
Group: Development/Libraries
Requires: bluez-libs = %{version}
Requires: pkgconfig
Obsoletes: bluez-sdp-devel < 4.0

%package cups
Summary: CUPS printer backend for Bluetooth printers
Group: System Environment/Daemons
Obsoletes: bluez-utils-cups < 4.5-2
Provides: bluez-utils-cups = %{version}-%{release}
Requires: bluez-libs = %{version}
Requires: cups

%package gstreamer
Summary: GStreamer support for SBC audio format
Group: System Environment/Daemons
Obsoletes: bluez-utils-gstreamer < 4.5-2
Provides: bluez-utils-gstreamer = %{version}-%{release}
Requires: bluez-libs = %{version}

%package alsa
Summary: ALSA support for Bluetooth audio devices
Obsoletes: bluez-utils-alsa < 4.5-2
Provides: bluez-utils-alsa = %{version}-%{release}
Group: System Environment/Daemons
Requires: bluez-libs = %{version}

%description cups
This package contains the CUPS backend 

%description gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%description alsa
This package contains ALSA support for Bluetooth audio devices

%description libs
Libraries for use in Bluetooth applications.

%description libs-devel
bluez-libs-devel contains development libraries and headers for
use in Bluetooth applications.

%prep

%setup -q
%patch1 -p0 -b .oui

%build
%configure --enable-cups --enable-hid2hci --enable-dfutool --enable-tools --enable-bccmd --enable-gstreamer --enable-hidd --enable-pand --enable-dund
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT 
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_libdir}
# Remove autocrap and libtool droppings
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la				\
	$RPM_BUILD_ROOT/%{_libdir}/alsa-lib/*.la		\
	$RPM_BUILD_ROOT/%{_libdir}/bluetooth/plugins/*.la	\
	$RPM_BUILD_ROOT/%{_libdir}/gstreamer-0.10/*.la

install -D -m0755 %SOURCE1 $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/bluetooth
install -D -m0644 %SOURCE2 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/bluetooth

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/cups
install -D -m0755 cups/bluetooth ${RPM_BUILD_ROOT}/usr/lib/cups/backend/bluetooth

install -D -m0755 scripts/bluetooth.rules ${RPM_BUILD_ROOT}/%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
install -D -m0755 scripts/bluetooth_serial ${RPM_BUILD_ROOT}/lib/udev/bluetooth_serial

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
/sbin/chkconfig --add bluetooth
if [ "$1" -ge "1" ]; then
	/sbin/service bluetooth condrestart >/dev/null 2>&1 || :
fi
exit 0

%postun libs -p /sbin/ldconfig

%preun
if [ "$1" = "0" ]; then
	/sbin/service bluetooth stop >/dev/null 2>&1 || :
	/sbin/chkconfig --del bluetooth
fi

%files
%defattr(-, root, root)
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*
%dir %{_sysconfdir}/bluetooth/
%config(noreplace) %{_sysconfdir}/bluetooth/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config %{_sysconfdir}/dbus-1/system.d/bluetooth.conf
%{_libdir}/bluetooth/plugins/*.so
/lib/udev/bluetooth_serial
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
/etc/rc.d/init.d/*

%files libs
%defattr(-, root, root)
%{_libdir}/libbluetooth.so.*
%doc AUTHORS COPYING INSTALL ChangeLog README

%files libs-devel
%defattr(-, root, root)
%{_libdir}/libbluetooth.so
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*
%{_libdir}/pkgconfig/bluez.pc

%files cups
%defattr(-, root, root)
/usr/lib/cups/backend/bluetooth

%files gstreamer
%defattr(-, root, root)
%{_libdir}/gstreamer-*/*.so

%files alsa
%defattr(-, root, root)
%{_libdir}/alsa-lib/*.so

%changelog
* Fri Oct 10 2008 - Bastien Nocera <bnocera@redhat.com> - 4.13-1
- Update to 4.13

* Mon Oct 06 2008 - Bastien Nocera <bnocera@redhat.com> - 4.12-1
- Update to 4.12

* Sat Oct 04 2008 - Bastien Nocera <bnocera@redhat.com> - 4.11-1
- Update to 4.11

* Fri Oct 03 2008 - Bastien Nocera <bnocera@redhat.com> - 4.10-1
- Update to 4.10

* Mon Sep 29 2008 - Bastien Nocera <bnocera@redhat.com> - 4.9-1
- Update to 4.9

* Mon Sep 29 2008 - Bastien Nocera <bnocera@redhat.com> - 4.8-1
- Update to 4.8

* Fri Sep 26 2008 - Bastien Nocera <bnocera@redhat.com> - 4.7-1
- Update to 4.7

* Wed Sep 24 2008 - Bastien Nocera <bnocera@redhat.com> - 4.6-4
- Fix patch application

* Wed Sep 24 2008 - Bastien Nocera <bnocera@redhat.com> - 4.6-3
- Add fuzz

* Wed Sep 24 2008 - Bastien Nocera <bnocera@redhat.com> - 4.6-2
- Fix possible crasher on resume from suspend

* Sun Sep 14 2008 - David Woodhouse <David.Woodhouse@intel.com> - 4.6-1
- Update to 4.6

* Fri Sep 12 2008 - David Woodhouse <David.Woodhouse@intel.com> - 4.5-4
- SDP browse fixes

* Fri Sep 12 2008 - David Woodhouse <David.Woodhouse@intel.com> - 4.5-3
- Bluez-alsa needs to provide/obsolete bluez-utils-alsa
- Use versioned Obsoletes:

* Fri Sep 12 2008 - David Woodhouse <David.Woodhouse@intel.com> - 4.5-2
- Change main utils package name to 'bluez'; likewise its subpackages
- Remove references to obsolete initscripts (hidd,pand,dund)

* Fri Sep 12 2008 - Bastien Nocera <bnocera@redhat.com> - 4.5-1
- Update to 4.5
- Fix initscript to actually start bluetoothd by hand
- Add chkconfig information to the initscript

* Tue Sep 09 2008 - David Woodhouse <David.Woodhouse@intel.com> - 4.4-2
- Fix rpmlint problems
- Fix input device handling

* Tue Sep 09 2008 - Bastien Nocera <bnocera@redhat.com> - 4.4-1
- Update to 4.4
- Update source address, and remove unneeded deps (thanks Marcel)

* Mon Aug 11 2008 - Bastien Nocera <bnocera@redhat.com> - 4.1-1
- Initial build
