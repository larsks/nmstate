// SPDX-License-Identifier: Apache-2.0

use std::collections::HashMap;

use crate::nm::nm_dbus::{NmConnection, NmSettingVpn};
use crate::{IpsecInterface, NetworkState};

pub(crate) fn gen_nm_ipsec_vpn_setting(
    iface: &IpsecInterface,
    nm_conn: &mut NmConnection,
) {
    if let Some(conf) = iface.libreswan.as_ref() {
        let mut vpn_data: HashMap<String, String> = HashMap::new();
        vpn_data.insert("right".into(), conf.right.to_string());
        if let Some(v) = conf.rightid.as_deref() {
            vpn_data.insert("rightid".into(), v.to_string());
        }
        if let Some(v) = conf.rightrsasigkey.as_deref() {
            vpn_data.insert("rightrsasigkey".into(), v.to_string());
        }
        if let Some(v) = conf.rightcert.as_deref() {
            vpn_data.insert("rightcert".into(), v.to_string());
        }
        if let Some(v) = conf.left.as_deref() {
            vpn_data.insert("left".into(), v.to_string());
        }
        if let Some(v) = conf.leftid.as_deref() {
            vpn_data.insert("leftid".into(), v.to_string());
        }
        if let Some(v) = conf.leftrsasigkey.as_deref() {
            vpn_data.insert("leftrsasigkey".into(), v.to_string());
        }
        if let Some(v) = conf.leftcert.as_deref() {
            vpn_data.insert("leftcert".into(), v.to_string());
        }
        if let Some(v) = conf.ikev2.as_deref() {
            vpn_data.insert("ikev2".into(), v.to_string());
        }
        if let Some(v) = conf.ikelifetime.as_deref() {
            vpn_data.insert("ikelifetime".into(), v.to_string());
        }
        if let Some(v) = conf.salifetime.as_deref() {
            vpn_data.insert("salifetime".into(), v.to_string());
        }
        if let Some(v) = conf.ike.as_deref() {
            vpn_data.insert("ike".into(), v.to_string());
        }
        if let Some(v) = conf.esp.as_deref() {
            vpn_data.insert("esp".into(), v.to_string());
        }
        if let Some(v) = conf.dpddelay {
            vpn_data.insert("dpddelay".into(), v.to_string());
        }
        if let Some(v) = conf.dpdtimeout {
            vpn_data.insert("dpdtimeout".into(), v.to_string());
        }
        if let Some(v) = conf.dpdaction.as_deref() {
            vpn_data.insert("dpdaction".into(), v.to_string());
        }
        if let Some(v) = conf.ipsec_interface.as_deref() {
            vpn_data.insert("ipsec-interface".into(), v.to_string());
        }
        if let Some(v) = conf.authby.as_deref() {
            vpn_data.insert("authby".into(), v.to_string());
        }
        if let Some(v) = conf.leftmodecfgclient {
            vpn_data.insert(
                "leftmodecfgclient".into(),
                if v {
                    "yes".to_string()
                } else {
                    "no".to_string()
                },
            );
        }
        if let Some(v) = conf.rightsubnet.as_deref() {
            vpn_data.insert("rightsubnet".into(), v.to_string());
        }
        if let Some(v) = conf.leftsubnet.as_deref() {
            vpn_data.insert("leftsubnet".into(), v.to_string());
        }
        if let Some(v) = conf.kind {
            vpn_data.insert("type".into(), v.to_string());
        }
        if let Some(v) = conf.clientaddrfamily {
            vpn_data.insert("clientaddrfamily".into(), v.to_string());
        }
        if let Some(v) = conf.hostaddrfamily {
            vpn_data.insert("hostaddrfamily".into(), v.to_string());
        }
        if let Some(v) = conf.require_id_on_certificate {
            let v = if v { "yes" } else { "no" };
            vpn_data.insert("require-id-on-certificate".into(), v.to_string());
        }

        let mut nm_vpn_set = NmSettingVpn::default();
        nm_vpn_set.data = Some(vpn_data);
        nm_vpn_set.service_type =
            Some(NmSettingVpn::SERVICE_TYPE_LIBRESWAN.to_string());
        if let Some(v) = conf.psk.as_deref() {
            if v == NetworkState::PASSWORD_HID_BY_NMSTATE {
                nm_vpn_set.secrets = nm_conn
                    .vpn
                    .as_ref()
                    .and_then(|c| c.secrets.as_ref())
                    .cloned();
            } else {
                nm_vpn_set
                    .secrets
                    .get_or_insert(HashMap::new())
                    .insert("pskvalue".to_string(), v.to_string());
            }
        }
        nm_conn.vpn = Some(nm_vpn_set);
    }
}
