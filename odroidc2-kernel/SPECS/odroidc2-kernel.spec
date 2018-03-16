%global commit_linux_long  c3e4c730feb1750940971cae9ca1da3ca50f1d56
%global commit_linux_short %(c=%{commit_linux_long}; echo ${c:0:7})                                                                                                                                                

%define Arch arm64
%define extra_version 6
%define _binaries_in_noarch_packages_terminate_build 0
%define debug_package %{nil}

Name:           odroidc2-kernel
Version:        3.14.79
Release:        %{extra_version}%{?dist}
BuildArch:	noarch
Summary:        Specific kernel for Odroid C2

License:        GPLv2
URL:            https://github.com/hardkernel/linux
Source0:        https://github.com/hardkernel/linux/tarball/%{commit_linux_long}
# https://github.com/mdrjr/c2_bootini/blob/master/c2_init.sh
Source1:        c2_init.sh
# http://forum.odroid.com/viewtopic.php?f=114&t=18768&p=124629
Source2:        module-setup.sh

Group:          System Environment/Kernel
Provides:       kernel = %{version}-%{release}
Requires:       dracut, coreutils, linux-firmware
Requires:       uboot-tools >= 2015.01
BuildRequires:  hostname, bc, devtoolset-3-gcc
#BuildRequires:

%description
Specific kernel for Odroid C2
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package devel
Group:          System Environment/Kernel
Summary:        Development package for building kernel modules to match the kernel
Provides:       kernel-devel = %{version}-%{release}

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.


#%package firmware
#Group:          Development/System
#Summary:        Firmware files used by the Linux kernel
#Provides:       kernel-firmware = %{version}-%{release}
#
#%description firmware
#Kernel-firmware includes firmware files required for some devices to
#operate.
# unused, firmware is in the linux-firmware noarch package

%prep
%setup -q -n hardkernel-linux-%{commit_linux_short}
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}/" Makefile

%build
/bin/scl enable devtoolset-3 - <<EOF
export KERNEL=kernel
make odroidc2_defconfig
make %{?_smp_mflags} Image dtbs modules
EOF

%install
mkdir -p %{buildroot}/boot/
mkdir -p %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot/overlays
cp -p -v COPYING %{buildroot}/boot/COPYING.linux
cp -p -v arch/%{Arch}/boot/dts/*.dtb %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot
cp -p -v arch/%{Arch}/boot/Image %{buildroot}/boot/Image-%{version}-%{release}
make INSTALL_MOD_PATH=%{buildroot} modules_install
rm -rf %{buildroot}/lib/firmware
mkdir -p %{buildroot}/usr/lib/dracut/modules.d/99c2_init/
cp -p -v %{SOURCE1} %{buildroot}/usr/lib/dracut/modules.d/99c2_init/
cp -p -v %{SOURCE2} %{buildroot}/usr/lib/dracut/modules.d/99c2_init/

# kernel-devel
DevelDir=/usr/src/kernels/%{version}-%{release}
mkdir -p %{buildroot}$DevelDir
# first copy everything
cp -p -v Module.symvers System.map %{buildroot}$DevelDir
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}$DevelDir
# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}$DevelDir/Documentation
rm -rf %{buildroot}$DevelDir/scripts
rm -rf %{buildroot}$DevelDir/include
cp .config %{buildroot}$DevelDir
cp -a scripts %{buildroot}$DevelDir
cp -a include %{buildroot}$DevelDir

if [ -d arch/%{Arch}/scripts ]; then
  cp -a arch/%{Arch}/scripts %{buildroot}$DevelDir/arch/%{_arch} || :
fi
if [ -f arch/%{Arch}/*lds ]; then
  cp -a arch/%{Arch}/*lds %{buildroot}$DevelDir/arch/%{_arch}/ || :
fi
rm -f %{buildroot}$DevelDir/scripts/*.o
rm -f %{buildroot}$DevelDir/scripts/*/*.o
cp -a --parents arch/%{Arch}/include %{buildroot}$DevelDir
# include the machine specific headers for ARM variants, if available.
if [ -d arch/%{Arch}/mach-exynos/include ]; then
  cp -a --parents arch/%{Arch}/mach-exynos/include %{buildroot}$DevelDir
fi
cp include/generated/uapi/linux/version.h %{buildroot}$DevelDir/include/linux
touch -r %{buildroot}$DevelDir/Makefile %{buildroot}$DevelDir/include/linux/version.h
ln -s $DevelDir %{buildroot}/lib/modules/%{version}-%{release}/build


%files
%defattr(-,root,root,-)
/lib/modules/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}/boot
#/usr/share/%{name}-kernel/%{version}-%{release}/boot/*.dtb
%attr(0755,root,root) /boot/Image-%{version}-%{release}
%doc /boot/COPYING.linux
%config /usr/lib/dracut/modules.d/99c2_init/

%post
cp -a /boot/Image-%{version}-%{release} /boot/Image
cp /usr/share/%{name}-kernel/%{version}-%{release}/boot/*.dtb /boot/
/usr/sbin/depmod -a %{version}-%{release}
dracut -H /boot/initrd-%{version}-%{release} %{version}-%{release}
mkimage -A %{Arch} -O linux -T ramdisk -C none -a 0 -e 0 \
	-n "uInitrd %{version}-%{release}" \
	-d /boot/initrd-%{version}-%{release} \
	/boot/uInitrd-%{version}-%{release}
cp -a /boot/uInitrd-%{version}-%{release} /boot/uInitrd

%preun
rm -f /boot/initrd-%{version}-%{release}
rm -f /boot/uInitrd-%{version}-%{release}

%postun
cp $(ls -1 /boot/uInitrd-*-*|tail -1) /boot/uInitrd
cp $(ls -1 /boot/Image-*-*|tail -1) /boot/Image
cp $(ls -1d /usr/share/%{name}-kernel/*-*/|tail -1)/boot/*.dtb /boot/


%files devel
%defattr(-,root,root)
/usr/src/kernels/%{version}-%{release}


#%files firmware
#%defattr(-,root,root)
#/lib/firmware/*

%changelog
* Fri Mar 16 2018 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-6
- updated to latest version on git. kernel version is the same though
- changed 99c2_init to a %config file. hopefully it'll install now

* Mon Nov 27 2017 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-5
- updated to latest version on git. kernel version is the same though

* Fri Oct 14 2016 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-4
- changed to noarch, so it'll also install on armv7 or armv5 systems

* Wed Oct 12 2016 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-3
- added c2_init to dracut
- added '-H' to dracut command
 
* Mon Oct 10 2016 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-2
- added requirement for uboot-tools >= 2015.01
- updated to the latest kernel from github
- changed the mkimage command to arm64

* Sun Oct 02 2016 Jacco Ligthart <jacco@redsleeve.org> - 3.14.79-1
- initial release for Odroid C2
