# Copyright 2015 Kitware, Inc.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

#  * Neither name of Kitware, Inc. nor the names of any contributors may be used
#    to endorse or promote products derived from this software without specific
#    prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Part of the DARPA PPAML CP6 toolset; poc: roddy.collins@kitware.com
#

##
## Utility routine
##

import sys
from cp6.utilities.image_indicator import ImageIndicator
from cp6.tables.image_indicator_table import ImageIndicatorTable
from cp6.tables.image_indicator_lookup_table import ImageIndicatorLookupTable

if len(sys.argv) != 4:
    sys.stderr.write( 'Usage: $0 image-indicator-lookup-table image-indicator-table image-id\n')
    sys.exit(0)

img_id = int(sys.argv[3])
iilut = ImageIndicatorLookupTable.read_from_file( sys.argv[1] )
sys.stderr.write( 'Info: IILUT has %d groups, %d tags\n' % (len(iilut.group_text_lut), len(iilut.tag_text_lut)))

iit = ImageIndicatorTable.read_from_file( sys.argv[2] )
sys.stderr.write( 'Info: IIT has %d images\n' % len(iit.image_indicators ))

if img_id not in iit.image_indicators:
    sys.stderr.write('Error: image ID %d not present in image indicator table\n' % img_id )
    sys.exit(1)

ii = iit.image_indicators[ img_id ]
(ngroups, nwords) = (len(ii.group_list), len(ii.word_list))
i = 1
for lut_id in sorted([int(x) for x in ii.group_list.keys()]):
    val = iilut.rev_lookup( 'G', lut_id )
    val = 'none' if not val else val
    sys.stdout.write('Group %d/%d: key %d, val %s\n' % (i, ngroups, lut_id, val ))
    i += 1
i = 1
for lut_id in sorted([int(x) for x in ii.word_list.keys()]):
    val = iilut.rev_lookup( 'W', lut_id )
    if not val:
        (val_str, flags_str) = ('none', 'none')
    else:
        val_str = val
        flags_str = ImageIndicator.flag2str( ii.word_source_flags[ lut_id ])
    sys.stdout.write('Word  %d/%d: key %d, val %s, flags: %s\n' % (i, nwords, lut_id, val_str, flags_str ))
    i += 1
