%global commit_linux_long  ec8448dd6e243e2e860dda8d514034b34875db97
%global commit_linux_short %(c=%{commit_linux_long}; echo ${c:0:7})

%define Arch arm
%define extra_version 1

Name:           odroidxu4-kernel
Version:        4.9.47
Release:        %{extra_version}%{?dist}
Summary:        Specific kernel for Odroid XU4

License:        GPLv2
URL:            https://github.com/hardkernel/linux
Source0:        https://github.com/hardkernel/linux/tarball/%{commit_linux_long}

Group:          System Environment/Kernel
Provides:       kernel = %{version}-%{release}
Requires:       dracut, uboot-tools, coreutils, linux-firmware
BuildRequires:	hostname, bc

# Compile with SELinux but disable per default
Patch0:		odroidxu3_selinux_config.patch
Patch1:		rtl8723du_CFLAGS.patch

%description
Specific kernel for Odroid XU4
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
%patch0 -p1
%patch1 -p1
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}/" Makefile

%build
export KERNEL=kernel
make odroidxu4_defconfig
make %{?_smp_mflags} zImage modules dtbs

%install
# kernel
mkdir -p %{buildroot}/boot/
mkdir -p %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot/overlays
cp -p -v COPYING %{buildroot}/boot/COPYING.linux
cp -p -v arch/arm/boot/dts/*.dtb %{buildroot}/usr/share/%{name}-kernel/%{version}-%{release}/boot
cp -p -v arch/arm/boot/zImage %{buildroot}/boot/zImage-%{version}-%{release}
make INSTALL_MOD_PATH=%{buildroot} modules_install
rm -rf %{buildroot}/lib/firmware

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
ln -T -s $DevelDir %{buildroot}/lib/modules/%{version}-%{release}/build --force
ln -T -s build %{buildroot}/lib/modules/%{version}-%{release}/source --force

%files
%defattr(-,root,root,-)
/lib/modules/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}
/usr/share/%{name}-kernel/%{version}-%{release}/boot
/usr/share/%{name}-kernel/%{version}-%{release}/boot/*.dtb
%attr(0755,root,root) /boot/zImage-%{version}-%{release}
%doc /boot/COPYING.linux

%post
cp /boot/zImage-%{version}-%{release} /boot/zImage
cp /usr/share/%{name}-kernel/%{version}-%{release}/boot/*.dtb /boot/
/usr/sbin/depmod -a %{version}-%{release}
dracut /boot/initrd-%{version}-%{release} %{version}-%{release}
mkimage -A arm -O linux -T ramdisk -C none -a 0 -e 0 \
	-n "uInitrd %{version}-%{release}" \
	-d /boot/initrd-%{version}-%{release} \
	/boot/uInitrd-%{version}-%{release}
cp /boot/uInitrd-%{version}-%{release} /boot/uInitrd

%preun
rm -f /boot/initrd-%{version}-%{release}
rm -f /boot/uInitrd-%{version}-%{release}

%postun
cp $(ls -1 /boot/uInitrd-*-*|tail -1) /boot/uInitrd
cp $(ls -1 /boot/zImage-*-*|tail -1) /boot/zImage
cp $(ls -1d /usr/share/%{name}-kernel/*-*/|tail -1)/boot/*.dtb /boot/


%files devel
%defattr(-,root,root)
/usr/src/kernels/%{version}-%{release}


#%files firmware
#%defattr(-,root,root)
#/lib/firmware/*

%changelog
* Fri Sep 08 2017 Jacco Ligthart <jacco@redsleeve.org>
- initial release for XU3/XU4
