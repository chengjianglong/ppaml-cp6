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


class ImageIndicator:
    #
    # Every image (via ID) gets one of these. It indicates the "relevant"
    # groups, words, and word-sources for the social media context of
    # the image. "Relevant" is defined by whether or not the (group, word)
    # appears in the IILUT.
    #
    # group_list, word_list, and word_source_flags are populated by
    # IILUT.add_to_indicator().
    #
    # group_list: key: IILUT id in group_table; value: 'True'
    #
    # word_list: key: IILUT id in word_table; value: 'True'
    #
    # word_source_flags: key: IILUT id in word_table; value: bitwise-OR of source flags
    #

    (IN_NONE, IN_TITLE, IN_DESC, IN_TAG, IN_COMMENT) = (0x0,0x01,0x02,0x04,0x08)
    def __init__( self, id ):
        self.id = id
        self.group_list = dict()
        self.word_list = dict()
        self.word_source_flags = dict()

    @staticmethod
    def flag2str( flag ):
        s = []
        if flag & ImageIndicator.IN_NONE:
            s.append("none")
        if flag & ImageIndicator.IN_TITLE:
            s.append("title")
        if flag & ImageIndicator.IN_DESC:
            s.append("description")
        if flag & ImageIndicator.IN_TAG:
            s.append("tag")
        if flag & ImageIndicator.IN_COMMENT:
            s.append("comment")
        return ",".join( s )

    def __str__( self ):
        return 'imageindicator %d: %d groups, %d words' % \
          (self.id, len(self.group_list), len(self.word_list))

