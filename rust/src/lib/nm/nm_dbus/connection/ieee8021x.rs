// SPDX-License-Identifier: Apache-2.0

use std::collections::HashMap;
use std::convert::TryFrom;

use serde::Deserialize;

use super::super::{
    connection::DbusDictionary, ErrorKind, NmError, ToDbusValue,
};

const GLIB_FILE_PATH_PREFIX: &str = "file://";

#[derive(Debug, Clone, PartialEq, Default, Deserialize)]
#[serde(try_from = "DbusDictionary")]
#[non_exhaustive]
pub struct NmSetting8021X {
    pub identity: Option<String>,
    pub private_key: Option<Vec<u8>>,
    pub eap: Option<Vec<String>>,
    pub client_cert: Option<Vec<u8>>,
    pub ca_cert: Option<Vec<u8>>,
    pub private_key_password: Option<String>,
    pub phase2_auth: Option<String>,
    pub password: Option<String>,
    _other: HashMap<String, zvariant::OwnedValue>,
}

impl TryFrom<DbusDictionary> for NmSetting8021X {
    type Error = NmError;
    fn try_from(mut v: DbusDictionary) -> Result<Self, Self::Error> {
        Ok(Self {
            identity: _from_map!(v, "identity", String::try_from)?,
            private_key: _from_map!(v, "private-key", <Vec<u8>>::try_from)?,
            eap: _from_map!(v, "eap", <Vec<String>>::try_from)?,
            client_cert: _from_map!(v, "client-cert", <Vec<u8>>::try_from)?,
            ca_cert: _from_map!(v, "ca-cert", <Vec<u8>>::try_from)?,
            private_key_password: None,
            phase2_auth: _from_map!(v, "phase2-auth", String::try_from)?,
            password: None,
            _other: v,
        })
    }
}

impl ToDbusValue for NmSetting8021X {
    fn to_value(&self) -> Result<HashMap<&str, zvariant::Value>, NmError> {
        let mut ret = HashMap::new();
        if let Some(v) = &self.identity {
            ret.insert("identity", zvariant::Value::new(v));
        }
        if let Some(v) = &self.private_key {
            ret.insert("private-key", zvariant::Value::new(v));
        }
        if let Some(v) = &self.eap {
            ret.insert("eap", zvariant::Value::new(v));
        }
        if let Some(v) = &self.client_cert {
            ret.insert("client-cert", zvariant::Value::new(v));
        }
        if let Some(v) = &self.ca_cert {
            ret.insert("ca-cert", zvariant::Value::new(v));
        }
        if let Some(v) = &self.private_key_password {
            ret.insert("private-key-password", zvariant::Value::new(v));
        }
        if let Some(v) = &self.phase2_auth {
            ret.insert("phase2-auth", zvariant::Value::new(v));
        }
        if let Some(v) = &self.password {
            ret.insert("password", zvariant::Value::new(v));
        }
        ret.extend(self._other.iter().map(|(key, value)| {
            (key.as_str(), zvariant::Value::from(value.clone()))
        }));
        Ok(ret)
    }
}

impl NmSetting8021X {
    #[cfg(feature = "query_apply")]
    pub(crate) fn fill_secrets(&mut self, secrets: &DbusDictionary) {
        if let Some(v) = secrets.get("private-key-password") {
            match String::try_from(v.clone()) {
                Ok(s) => {
                    self.private_key_password = Some(s);
                }
                Err(e) => {
                    log::warn!(
                        "Failed to convert private_key_password: \
                        {:?} {:?}",
                        v,
                        e
                    );
                }
            }
        }
        if let Some(v) = secrets.get("password") {
            match String::try_from(v.clone()) {
                Ok(s) => {
                    self.password = Some(s);
                }
                Err(e) => {
                    log::warn!(
                        "Failed to convert password: \
                        {:?} {:?}",
                        v,
                        e
                    );
                }
            }
        }
    }

    pub fn file_path_to_glib_bytes(file_path: &str) -> Vec<u8> {
        format!("{GLIB_FILE_PATH_PREFIX}{file_path}\0").into_bytes()
    }

    pub fn glib_bytes_to_file_path(value: &[u8]) -> Result<String, NmError> {
        let mut file_path = match String::from_utf8(value.to_vec()) {
            Ok(f) => f.trim_end_matches(char::from(0)).to_string(),
            Err(e) => {
                let e = NmError::new(
                    ErrorKind::InvalidArgument,
                    format!(
                        "Failed to parse glib bytes to UTF-8 string: \
                        {value:?}: {e:?}"
                    ),
                );
                log::error!("{}", e);
                return Err(e);
            }
        };
        if file_path.starts_with(GLIB_FILE_PATH_PREFIX) {
            file_path.drain(..GLIB_FILE_PATH_PREFIX.len());
            Ok(file_path)
        } else {
            let e = NmError::new(
                ErrorKind::InvalidArgument,
                format!(
                    "Specified glib bytes is started with {GLIB_FILE_PATH_PREFIX}: {value:?}"
                ),
            );
            log::error!("{}", e);
            Err(e)
        }
    }
}
