// SPDX-License-Identifier: Apache-2.0

use crate::{BaseInterface, VrfConfig, VrfInterface};

pub(crate) fn np_vrf_to_nmstate(
    np_iface: &nispor::Iface,
    base_iface: BaseInterface,
) -> VrfInterface {
    let vrf_conf = np_iface.vrf.as_ref().map(|np_vrf_info| VrfConfig {
        table_id: Some(np_vrf_info.table_id),
        port: {
            let mut ports = np_vrf_info.subordinates.clone();
            ports.sort_unstable();
            Some(ports)
        },
    });

    VrfInterface {
        base: base_iface,
        vrf: vrf_conf,
    }
}
