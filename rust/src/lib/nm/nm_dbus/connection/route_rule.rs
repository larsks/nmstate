// SPDX-License-Identifier: Apache-2.0

// Copyright 2021 Red Hat, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

use std::convert::TryFrom;

use serde::Deserialize;

use super::super::{connection::DbusDictionary, error::NmError};

#[derive(Debug, Clone, PartialEq, Default, Deserialize)]
#[serde(try_from = "DbusDictionary")]
#[non_exhaustive]
pub struct NmIpRouteRule {
    pub family: Option<i32>,
    pub priority: Option<u32>,
    pub from: Option<String>,
    pub from_len: Option<u8>,
    pub to: Option<String>,
    pub to_len: Option<u8>,
    pub table: Option<u32>,
    pub fw_mark: Option<u32>,
    pub fw_mask: Option<u32>,
    pub iifname: Option<String>,
    pub action: Option<NmIpRouteRuleAction>,
    pub suppress_prefixlength: Option<i32>,
    _other: DbusDictionary,
}

impl TryFrom<DbusDictionary> for NmIpRouteRule {
    type Error = NmError;
    fn try_from(mut v: DbusDictionary) -> Result<Self, Self::Error> {
        Ok(Self {
            family: _from_map!(v, "family", i32::try_from)?,
            priority: _from_map!(v, "priority", u32::try_from)?,
            from: _from_map!(v, "from", String::try_from)?,
            from_len: _from_map!(v, "from-len", u8::try_from)?,
            to: _from_map!(v, "to", String::try_from)?,
            to_len: _from_map!(v, "to-len", u8::try_from)?,
            table: _from_map!(v, "table", u32::try_from)?,
            fw_mark: _from_map!(v, "fwmark", u32::try_from)?,
            fw_mask: _from_map!(v, "fwmask", u32::try_from)?,
            iifname: _from_map!(v, "iifname", String::try_from)?,
            action: _from_map!(v, "action", u8::try_from)?
                .map(NmIpRouteRuleAction::from),
            suppress_prefixlength: _from_map!(
                v,
                "suppress-prefixlength",
                i32::try_from
            )?,
            _other: v,
        })
    }
}

impl NmIpRouteRule {
    pub(crate) fn to_value(&self) -> Result<zvariant::Value, NmError> {
        let mut ret = zvariant::Dict::new(
            zvariant::Signature::from_str_unchecked("s"),
            zvariant::Signature::from_str_unchecked("v"),
        );
        if let Some(v) = &self.family {
            ret.append(
                zvariant::Value::new("family"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.priority {
            ret.append(
                zvariant::Value::new("priority"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.from {
            ret.append(
                zvariant::Value::new("from"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.from_len {
            ret.append(
                zvariant::Value::new("from-len"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.to {
            ret.append(
                zvariant::Value::new("to"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.to_len {
            ret.append(
                zvariant::Value::new("to-len"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.table {
            ret.append(
                zvariant::Value::new("table"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.fw_mark {
            ret.append(
                zvariant::Value::new("fwmark"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.fw_mask {
            ret.append(
                zvariant::Value::new("fwmask"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.iifname {
            ret.append(
                zvariant::Value::new("iifname"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }
        if let Some(v) = &self.action {
            ret.append(
                zvariant::Value::new("action"),
                zvariant::Value::new(zvariant::Value::new(u8::from(*v))),
            )?;
        }
        if let Some(v) = &self.suppress_prefixlength {
            ret.append(
                zvariant::Value::new("suppress-prefixlength"),
                zvariant::Value::new(zvariant::Value::new(v)),
            )?;
        }

        for (key, value) in self._other.iter() {
            ret.append(
                zvariant::Value::new(key.as_str()),
                zvariant::Value::from(value.clone()),
            )?;
        }
        Ok(zvariant::Value::Dict(ret))
    }
}

pub(crate) fn parse_nm_ip_rule_data(
    value: zvariant::OwnedValue,
) -> Result<Vec<NmIpRouteRule>, NmError> {
    let mut rules = Vec::new();
    for nm_rule_value in <Vec<DbusDictionary>>::try_from(value)? {
        rules.push(NmIpRouteRule::try_from(nm_rule_value)?);
    }
    Ok(rules)
}

pub(crate) fn nm_ip_rules_to_value(
    nm_rules: &[NmIpRouteRule],
) -> Result<zvariant::Value, NmError> {
    let mut rule_values =
        zvariant::Array::new(zvariant::Signature::from_str_unchecked("a{sv}"));
    for nm_rule in nm_rules {
        rule_values.append(nm_rule.to_value()?)?;
    }
    Ok(zvariant::Value::Array(rule_values))
}

const RTN_BLACKHOLE: u8 = 6;
const RTN_UNREACHABLE: u8 = 7;
const RTN_PROHIBIT: u8 = 8;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[non_exhaustive]
pub enum NmIpRouteRuleAction {
    Blackhole,
    Unreachable,
    Prohibit,
    Other(u8),
}

impl From<u8> for NmIpRouteRuleAction {
    fn from(v: u8) -> Self {
        match v {
            RTN_BLACKHOLE => Self::Blackhole,
            RTN_UNREACHABLE => Self::Unreachable,
            RTN_PROHIBIT => Self::Prohibit,
            _ => {
                log::warn!("Unsupported IP route rule action {}", v);
                Self::Other(v)
            }
        }
    }
}

impl From<NmIpRouteRuleAction> for u8 {
    fn from(v: NmIpRouteRuleAction) -> Self {
        match v {
            NmIpRouteRuleAction::Blackhole => RTN_BLACKHOLE,
            NmIpRouteRuleAction::Unreachable => RTN_UNREACHABLE,
            NmIpRouteRuleAction::Prohibit => RTN_PROHIBIT,
            NmIpRouteRuleAction::Other(d) => d,
        }
    }
}

impl std::fmt::Display for NmIpRouteRuleAction {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            NmIpRouteRuleAction::Blackhole => write!(f, "blackhole"),
            NmIpRouteRuleAction::Unreachable => write!(f, "unreachable"),
            NmIpRouteRuleAction::Prohibit => write!(f, "prohibit"),
            NmIpRouteRuleAction::Other(d) => write!(f, "{}", d),
        }
    }
}
