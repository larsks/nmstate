// SPDX-License-Identifier: Apache-2.0

use std::collections::HashMap;
use std::convert::TryFrom;

use serde::Deserialize;

use super::super::{connection::DbusDictionary, NmError, ToDbusValue};

#[derive(Debug, Clone, PartialEq, Default, Deserialize)]
#[serde(try_from = "DbusDictionary")]
#[non_exhaustive]
pub struct NmSettingIpVlan {
    pub parent: Option<String>,
    pub mode: Option<u32>,
    pub private: Option<bool>,
    pub vepa: Option<bool>,
    _other: HashMap<String, zvariant::OwnedValue>,
}

impl TryFrom<DbusDictionary> for NmSettingIpVlan {
    type Error = NmError;
    fn try_from(mut v: DbusDictionary) -> Result<Self, Self::Error> {
        Ok(Self {
            parent: _from_map!(v, "parent", String::try_from)?,
            mode: _from_map!(v, "mode", u32::try_from)?,
            private: _from_map!(v, "private", bool::try_from)?,
            vepa: _from_map!(v, "vepa", bool::try_from)?,
            _other: v,
        })
    }
}

impl ToDbusValue for NmSettingIpVlan {
    fn to_value(&self) -> Result<HashMap<&str, zvariant::Value>, NmError> {
        let mut ret = HashMap::new();
        if let Some(v) = &self.parent {
            ret.insert("parent", zvariant::Value::new(v.clone()));
        }
        if let Some(v) = self.mode {
            ret.insert("mode", zvariant::Value::new(v));
        }
        if let Some(v) = self.private {
            ret.insert("private", zvariant::Value::new(v));
        }
        if let Some(v) = self.vepa {
            ret.insert("vepa", zvariant::Value::new(v));
        }
        ret.extend(self._other.iter().map(|(key, value)| {
            (key.as_str(), zvariant::Value::from(value.clone()))
        }));
        Ok(ret)
    }
}
