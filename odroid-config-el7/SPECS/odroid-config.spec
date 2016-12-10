Name:           odroid-config
Version:        0.1
Release:        1%{?dist}
Summary:        specific configuration of Redsleeve Linux on Odroid's
BuildArch:      noarch

License:        GPL
URL:            n/a
Source0:        odroid.repo


%description
Specific configuration of Redsleeve Linux on the Odroid U3

%install
mkdir -p %{buildroot}/etc/yum.repos.d
cp %{SOURCE0} %{buildroot}/etc/yum.repos.d


%files
%defattr(-,root,root)
%config /etc/yum.repos.d/odroid.repo


%changelog
* Fri Sep 30 2016 Jacco Ligthart <jacco@redsleeve.org> - 0.1
- initial version
