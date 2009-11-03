Summary: Bluetooth utilities
Name: bluez
Version: 4.42
Release: 9%{?dist}
License: GPLv2+
Group: Applications/System
Source: http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.gz
Source1: bluetooth.init
Source2: bluez-uinput.modules
Patch1: bluez-utils-oui-usage.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=450081
# http://thread.gmane.org/gmane.linux.bluez.kernel/1687
Patch2: bluez-try-utf8-harder.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/1754
Patch3: bluez-activate-wacom-mode2.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=498756
Patch4: bluez-socket-mobile-cf-connection-kit.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=507572
Patch5: cups-less-errors.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/3108
Patch6: 0001-Don-t-abort-cups-backend-on-property-change.patch
Patch7: 0002-Actually-read-the-CreateDevice-reply.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/3106/focus=3114
Patch8: 0001-Allow-lp-CUPS-to-talk-to-bluetoothd.patch
Patch9: 0002-Mark-Bluetooth-printers-as-being-local.patch
# Updated from udev-extras master
Patch10: bluez-4.42-update-hid2hci-rules.patch
Patch11: bluez-4.42-make-udev-helper-build.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: http://www.bluez.org/

BuildRequires: flex
BuildRequires: dbus-devel >= 0.90
BuildRequires: libusb-devel, glib2-devel, alsa-lib-devel
BuildRequires: gstreamer-plugins-base-devel, gstreamer-devel
BuildRequires: libsndfile-devel
BuildRequires: libudev-devel

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
%patch2 -p1 -b .non-utf8-name
%patch3 -p1 -b .wacom
%patch4 -p1 -b .socket-mobile
%patch5 -p1 -b .cups-less-errors
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1

%build
%configure --enable-cups --disable-hid2hci --enable-dfutool --enable-tools --enable-bccmd --enable-gstreamer --enable-hidd --enable-pand --enable-dund
make

# Build by hand...
pushd tools
gcc -o hid2hci -DUTIL_PATH_SIZE=4096 -DLIBUDEV_I_KNOW_THE_API_IS_SUBJECT_TO_CHANGE=1 `pkg-config --libs --cflags libudev libusb` hid2hci.c
popd

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

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
if test -d ${RPM_BUILD_ROOT}/usr/lib64/cups ; then
	install -D -m0755 ${RPM_BUILD_ROOT}/usr/lib64/cups/backend/bluetooth ${RPM_BUILD_ROOT}/usr/lib/cups/backend/bluetooth
	rm -rf ${RPM_BUILD_ROOT}%{_libdir}/cups
fi

install -D -m0644 scripts/bluetooth-serial.rules ${RPM_BUILD_ROOT}/%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
install -D -m0755 scripts/bluetooth_serial ${RPM_BUILD_ROOT}/lib/udev/bluetooth_serial

# Install hid2hci
install -D -m0644 scripts/bluetooth-hid2hci.rules ${RPM_BUILD_ROOT}/lib/udev/rules.d/70-hid2hci.rules
install -D -m0755 tools/hid2hci ${RPM_BUILD_ROOT}/lib/udev/hid2hci

install -D -m0755 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/modules/bluez-uinput.modules

install -d -m0755 $RPM_BUILD_ROOT/%{_localstatedir}/lib/bluetooth

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
%config %{_sysconfdir}/dbus-1/system.d/bluetooth.conf
%{_libdir}/bluetooth/
/lib/udev/bluetooth_serial
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
/lib/udev/rules.d/*.rules
/lib/udev/hid2hci
/etc/rc.d/init.d/*
%{_localstatedir}/lib/bluetooth
%{_sysconfdir}/sysconfig/modules/bluez-uinput.modules

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
%{_sysconfdir}/alsa/bluetooth.conf

%changelog
* Tue Nov 03 2009 Bastien Nocera <bnocera@redhat.com> 4.42-9
- Update hid2hci udev rules for F11 udev

* Mon Nov 02 2009 Bastien Nocera <bnocera@redhat.com> 4.42-8
- Update hid2hci code from udev master

* Wed Sep 16 2009 Bastien Nocera <bnocera@redhat.com> 4.42-7
- Backport code to re-enable Dell HID proxies (#513103)

* Wed Sep 16 2009 Bastien Nocera <bnocera@redhat.com> 4.42-6
- Fix hid2hci rules (#517088)

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 4.42-5
- More upstream CUPS fixes

* Tue Aug 11 2009 Bastien Nocera <bnocera@redhat.com> 4.42-4
- Fix cups discovery the first time we discover a device

* Mon Aug 03 2009 Bastien Nocera <bnocera@redhat.com> 4.42-3
- Fix hid2hci rules location

* Mon Aug 03 2009 Bastien Nocera <bnocera@redhat.com> 4.42-2
- Let udev rules handle hid2hci (#514698)

* Wed Jun 24 2009 Bastien Nocera <bnocera@redhat.com> 4.42-1
- Update to 4.42

* Wed Jun 24 2009 Bastien Nocera <bnocera@redhat.com> 4.37-4
- Reduce the number of errors from CUPS when bluetoothd
  isn't running, or there's no adapters (#507572)

* Fri May 08 2009 Bastien Nocera <bnocera@redhat.com> 4.37-3
- Hopefully fix HID device not reconnecting properly after
  they've been disconnected (#485927)

* Tue May 05 2009 Bastien Nocera <bnocera@redhat.com> 4.37-2
- Add patch to activate the Socket Mobile CF kit (#498756)

* Thu Apr 23 2009 - Bastien Nocera <bnocera@redhat.com> - 4.37-1
- Update to 4.37

* Fri Apr 17 2009 - Bastien Nocera <bnocera@redhat.com> - 4.36-1
- Update to 4.36

* Sat Apr 11 2009 - Bastien Nocera <bnocera@redhat.com> - 4.35-1
- Update to 4.35

* Fri Apr 03 2009 - Bastien Nocera <bnocera@redhat.com> - 4.34-3
- Avoid disconnecting audio devices straight after they're connected

* Fri Apr 03 2009 - Bastien Nocera <bnocera@redhat.com> - 4.34-2
- Don't crash when audio devices are registered and the adapter
  is removed

* Sun Mar 29 2009 - Bastien Nocera <bnocera@redhat.com> - 4.34-1
- Update to 4.34

* Tue Mar 24 2009 - Bastien Nocera <bnocera@redhat.com> - 4.33-11
- Fix a possible crasher

* Mon Mar 16 2009 - Bastien Nocera <bnocera@redhat.com> - 4.33-1
- Update to 4.33

* Sat Mar 14 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-10
- Fix a couple of warnings in the CUPS/BlueZ 4.x patch

* Fri Mar 13 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-9
- Switch Wacom Bluetooth tablet to mode 2

* Mon Mar 09 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-8
- Port CUPS backend to BlueZ 4.x

* Mon Mar 09 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-7
- A (slightly) different fix for parsing to XML when it contains a NULL

* Mon Mar 09 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-6
- Fix sdp_copy_record(), so records are properly exported through D-Bus

* Fri Mar 06 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-5
- Fix SDP parsing to XML when it contains NULLs

* Thu Mar 05 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-4
- Work-around broken devices that export their names in ISO-8859-1
  (#450081)

* Thu Mar 05 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-3
- Fix permissions on the udev rules (#479348)

* Wed Mar 04 2009 - Bastien Nocera <bnocera@redhat.com> - 4.32-2
- Own /usr/lib*/bluetooth and children (#474632)

* Mon Mar 2 2009 Lennart Poettering <lpoetter@redhat.com> - 4.32-1
- Update to 4.32

* Thu Feb 26 2009 Lennart Poettering <lpoetter@redhat.com> - 4.31-1
- Update to 4.31

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.30-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 - Bastien Nocera <bnocera@redhat.com> - 4.30-2
- Fix the cups backend being a libtool stub

* Thu Feb 12 2009 - Bastien Nocera <bnocera@redhat.com> - 4.30-1
- Update to 4.30

* Thu Feb 12 2009 Karsten Hopp <karsten@redhat.com> 4.29-3
- disable 0001-Add-icon-for-other-audio-device.patch, already upstream

* Thu Feb 12 2009 Karsten Hopp <karsten@redhat.com> 4.29-2
- bluez builds fine on s390(x) and the packages are required to build
  other packages, drop ExcludeArch

* Mon Feb 09 2009 - Bastien Nocera <bnocera@redhat.com> - 4.29-1
- Update to 4.29

* Mon Feb 02 2009 - Bastien Nocera <bnocera@redhat.com> - 4.28-1
- Update to 4.28

* Mon Jan 19 2009 - Bastien Nocera <bnocera@redhat.com> - 4.27-1
- Update to 4.27

* Fri Jan 09 2009 - Bastien Nocera <bnocera@redhat.com> - 4.26-1
- Update to 4.26

* Sat Jan 03 2009 - Bastien Nocera <bnocera@redhat.com> - 4.25-1
- Update to 4.25

* Tue Dec 09 2008 - Bastien Nocera <bnocera@redhat.com> - 4.22-2
- Fix D-Bus configuration for latest D-Bus (#475069)

* Mon Dec 08 2008 - Bastien Nocera <bnocera@redhat.com> - 4.22-1
- Update to 4.22

* Mon Dec 01 2008 - Bastien Nocera <bnocera@redhat.com> - 4.21-1
- Update to 4.21

* Fri Nov 21 2008 - Bastien Nocera <bnocera@redhat.com> - 4.19-1
- Update to 4.19

* Mon Nov 17 2008 - Bastien Nocera <bnocera@redhat.com> - 4.18-1
- Update to 4.18

* Mon Oct 27 2008 - Bastien Nocera <bnocera@redhat.com> - 4.17-2
- Own /var/lib/bluetooth (#468717)

* Sun Oct 26 2008 - Bastien Nocera <bnocera@redhat.com> - 4.17-1
- Update to 4.17

* Tue Oct 21 2008 - Bastien Nocera <bnocera@redhat.com> - 4.16-1
- Update to 4.16

* Mon Oct 20 2008 - Bastien Nocera <bnocera@redhat.com> - 4.15-1
- Update to 4.15

* Fri Oct 17 2008 - Bastien Nocera <bnocera@redhat.com> - 4.14-2
- Add script to autoload uinput on startup, so the PS3 remote
  works out-of-the-box

* Fri Oct 17 2008 - Bastien Nocera <bnocera@redhat.com> - 4.14-1
- Update to 4.14

* Tue Oct 14 2008 - Bastien Nocera <bnocera@redhat.com> - 4.13-3
- Update udev rules (#246840)

* Mon Oct 13 2008 - Bastien Nocera <bnocera@redhat.com> - 4.13-2
- Fix PS3 BD remote input event generation

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
