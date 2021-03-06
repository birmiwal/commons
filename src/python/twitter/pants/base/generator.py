# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

from __future__ import print_function

import pprint
import pystache


def _expand(map):
  # Add foo? for each foo in the map that evaluates to true.
  # Mustache needs this, especially in cases where foo is a list: there is no way to render a
  # block exactly once iff a list is not empty.
  # Note: if the original map contains foo?, it will take precedence over our synthetic foo?.
  def set_to_map(x):
    # Pystache can't handle sets, so we convert to maps of key->True.
    if isinstance(x, set):
      return dict([(k, True) for k in x])
    else:
      return x
  items = [(key, set_to_map(val)) for (key, val) in map.items()]
  ret = dict([(key + '?', True) for (key, val) in items if val and not key.endswith('?')])
  ret.update(dict(items))
  return ret

class TemplateData(dict):
  """Encapsulates data for a mustache template as a property-addressable read-only map-like struct."""

  def __init__(self, **kwargs):
    dict.__init__(self, _expand(kwargs))

  def extend(self, **kwargs):
    """Returns a new TemplateData with this template's data overlayed by the key value pairs
    specified as keyword arguments."""

    props = self.copy()
    props.update(kwargs)
    return TemplateData(**props)

  def __setattr__(self, key, value):
    raise AttributeError("Mutation not allowed - use %s.extend(%s = %s)" % (self, key, value))

  def __getattr__(self, key):
    if key in self:
      return self[key]
    else:
      return object.__getattribute__(self, key)

  def __str__(self):
    return 'TemplateData(%s)' % pprint.pformat(self)

class Generator(object):
  """Generates pants intermediary output files using a configured mustache template."""

  def __init__(self, template_text, **template_data):
    self._template =  pystache.parse(unicode(template_text))
    self.template_data = template_data

  def write(self, stream):
    """Applies the template to the template data and writes the result to the given file-like
    stream."""
    stream.write(pystache.render(self._template, self.template_data))

