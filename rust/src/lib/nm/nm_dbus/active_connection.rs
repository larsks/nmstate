// SPDX-License-Identifier: Apache-2.0

use super::NmIfaceType;
#[cfg(feature = "query_apply")]
use super::{
    connection::nm_con_get_from_obj_path,
    dbus::{obj_path_to_string, NM_DBUS_INTERFACE_AC, NM_DBUS_INTERFACE_ROOT},
    ErrorKind, NmError,
};

pub const NM_ACTIVATION_STATE_FLAG_EXTERNAL: u32 = 0x80;

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct NmActiveConnection {
    pub uuid: String,
    pub iface_type: NmIfaceType,
    pub iface_name: String,
    pub state_flags: u32,
}

#[cfg(feature = "query_apply")]
fn nm_ac_obj_path_state_flags_get(
    dbus_conn: &zbus::Connection,
    obj_path: &str,
) -> Result<u32, NmError> {
    let proxy = zbus::Proxy::new(
        dbus_conn,
        NM_DBUS_INTERFACE_ROOT,
        obj_path,
        NM_DBUS_INTERFACE_AC,
    )?;
    match proxy.get_property::<u32>("StateFlags") {
        Ok(uuid) => Ok(uuid),
        Err(e) => Err(NmError::new(
            ErrorKind::Bug,
            format!(
                "Failed to retrieve StateFlags of active connection {obj_path}: {e}"
            ),
        )),
    }
}

#[cfg(feature = "query_apply")]
pub(crate) fn nm_ac_obj_path_uuid_get(
    dbus_conn: &zbus::Connection,
    obj_path: &str,
) -> Result<String, NmError> {
    let proxy = zbus::Proxy::new(
        dbus_conn,
        NM_DBUS_INTERFACE_ROOT,
        obj_path,
        NM_DBUS_INTERFACE_AC,
    )?;
    match proxy.get_property::<String>("Uuid") {
        Ok(uuid) => Ok(uuid),
        Err(e) => Err(NmError::new(
            ErrorKind::Bug,
            format!(
                "Failed to retrieve UUID of active connection {obj_path}: {e}"
            ),
        )),
    }
}

#[cfg(feature = "query_apply")]
fn nm_ac_obj_path_nm_con_obj_path_get(
    dbus_conn: &zbus::Connection,
    obj_path: &str,
) -> Result<String, NmError> {
    let proxy = zbus::Proxy::new(
        dbus_conn,
        NM_DBUS_INTERFACE_ROOT,
        obj_path,
        NM_DBUS_INTERFACE_AC,
    )?;
    match proxy.get_property::<zvariant::OwnedObjectPath>("Connection") {
        Ok(p) => Ok(obj_path_to_string(p)),
        // Sometimes the Active Connection is deleting or deactivating which
        // does not have connection associated, we return "" in this case
        Err(_) => Ok("".to_string()),
    }
}

#[cfg(feature = "query_apply")]
pub(crate) fn get_nm_ac_by_obj_path(
    connection: &zbus::Connection,
    obj_path: &str,
) -> Result<Option<NmActiveConnection>, NmError> {
    // Sometimes the Active Connection is deleting or deactivating which
    // does not have connection associated, we return None in this case
    let nm_conn_obj_path =
        nm_ac_obj_path_nm_con_obj_path_get(connection, obj_path)?;

    if (!nm_conn_obj_path.is_empty()) && nm_conn_obj_path != "/" {
        let nm_conn = nm_con_get_from_obj_path(connection, &nm_conn_obj_path)?;
        let iface_name = match nm_conn.iface_name() {
            Some(i) => i.to_string(),
            None => "".to_string(),
        };
        let iface_type = nm_conn.iface_type().cloned().unwrap_or_default();
        Ok(Some(NmActiveConnection {
            uuid: nm_ac_obj_path_uuid_get(connection, obj_path)?,
            iface_name,
            iface_type,
            state_flags: nm_ac_obj_path_state_flags_get(connection, obj_path)?,
        }))
    } else {
        Ok(None)
    }
}
