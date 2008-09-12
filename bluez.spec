Summary: Bluetooth libraries and utilities
Name: bluez
Version: 4.5
Release: 1%{?dist}
License: GPLv2+
Group: System Environment/Libraries
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

%description
Libraries and utilities for use in Bluetooth applications.

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

%package utils-cups
Summary: CUPS printer backend for Bluetooth printers
Group: System Environment/Daemons
Requires: bluez-libs = %{version}
Requires: cups

%package utils-gstreamer
Summary: GStreamer support for SBC audio format
Group: System Environment/Daemons
Requires: bluez-libs = %{version}

%package utils-alsa
Summary: ALSA support for Bluetooth audio devices
Group: System Environment/Daemons
Requires: bluez-libs = %{version}

%package utils
Summary: Bluetooth utilities
Group: Applications/System
Obsoletes: bluez-pan < 4.0, bluez-sdp < 4.0
Requires: initscripts, bluez-libs = %{version}
Requires: dbus >= 0.60
Requires: hwdata >= 0.215
Requires: dbus-bluez-pin-helper
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(post): /sbin/chkconfig, /sbin/service

%description utils-cups
This package contains the CUPS backend 

%description utils-gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%description utils-alsa
This package contains ALSA support for Bluetooth audio devices

%description libs
Libraries for use in Bluetooth applications.

%description libs-devel
bluez-libs-devel contains development libraries and headers for
use in Bluetooth applications.

%description utils
Bluetooth utilities (bluez-utils):
	- hcitool
	- hciattach
	- hciconfig
	- hcid
	- l2ping
	- start scripts (Red Hat)
	- pcmcia configuration files

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
rm -f $RPM_BUILD_ROOT/usr/share/aclocal/bluez.m4

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

%post utils
/sbin/chkconfig --del hidd >/dev/null 2>&1 || :
/sbin/chkconfig --del dund >/dev/null 2>&1 || :
/sbin/chkconfig --del pand >/dev/null 2>&1 || :

/sbin/chkconfig --add bluetooth
if [ "$1" -ge "1" ]; then
	/sbin/service bluetooth condrestart >/dev/null 2>&1 || :
fi
exit 0

%postun libs -p /sbin/ldconfig

%preun utils
if [ "$1" = "0" ]; then
	/sbin/service bluetooth stop >/dev/null 2>&1 || :
	/sbin/service dund stop >/dev/null 2>&1 || :
	/sbin/service pand stop >/dev/null 2>&1 || :
	/sbin/chkconfig --del bluetooth
	/sbin/chkconfig --del dund 2>&1 || :
	/sbin/chkconfig --del pand 2>&1 || :
fi

%files utils
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

%files utils-cups
%defattr(-, root, root)
/usr/lib/cups/backend/bluetooth

%files utils-gstreamer
%defattr(-, root, root)
%{_libdir}/gstreamer-*/*.so

%files utils-alsa
%defattr(-, root, root)
%{_libdir}/alsa-lib/*.so

%changelog
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
