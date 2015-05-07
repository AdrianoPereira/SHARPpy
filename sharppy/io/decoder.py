
import numpy as np

import sharppy.sharptab.profile as profile

import urllib2
from datetime import datetime

class abstract(object):
    def __init__(self, func):
        self._func = func
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Function or method '%s' is abstract.  Override it in a subclass!" % self._func.__name__)

# Comment this file
# Move inherited decoders to ~/.sharppy/decoders
# Write function to figure out what custom decoders we have

class Decoder(object):
    def __init__(self, file_name):
        self._profiles, self._dates = self._parse(file_name)

    @abstract
    def _parse(self):
        pass

    def _downloadFile(self, file_name):
        # Try to open the file.  This is a dirty hack right now until
        # I can figure out a cleaner way to make sure the file (either local or URL)
        # gets opened.
        try:
            f = urllib2.urlopen(file_name)
        except (ValueError, IOError):
            try:
                f = open(file_name, 'r')
            except IOError:
                raise IOError("File '%s' cannot be found" % file_name)
        file_data = f.read()
#       f.close() # Apparently, this multiplies the time this function takes by anywhere from 2 to 6 ... ???
        return file_data

    def getProfiles(self, prof_idxs=[0], prog=None, prof_type='default'):
        '''
            Returns a list of profile objects generated from the
            file that was read in.

            Parameters
            ----------
            prof_idxs : list (optional)
                A list of indices corresponding to the profiles to be returned.
                Default is [0]
            prog : flag
                A flag that indicates whether or not the data source is prognostic

        '''
        profiles = []
        mean_idx = 0
        for idx, (mem_name, mem_profs) in enumerate(self._profiles.iteritems()):
            profs = []
            nprofs = len(mem_profs) if prof_idxs is None else len(prof_idxs)

            for pidx, prof_idx in enumerate(prof_idxs):
                # If the member name is the mean profile, or there
                # is only one profile recorded in the file, then get the index.
                if 'mean' in mem_name.lower() or len(self._profiles) == 1:
                    mean_idx = idx
                    if prog is not None:
                        prog.emit(pidx, nprofs)
                    profs.append(profile.ConvectiveProfile.copy(mem_profs[prof_idx]))
                else:
                    if prof_type == 'default':
                        profs.append(profile.BasicProfile.copy(mem_profs[prof_idx]))
                    elif prof_type == 'vad':
                        profs.append(mem_profs[prof_idx])

            profiles.append(profs)

        mean = profiles[mean_idx]

        # Rearrange list of profiless so the mean is the first element.
        profiles = [ mean ] + profiles[:mean_idx] + profiles[(mean_idx + 1):]

        if len(profiles) > 1:
            profiles = [ list(p) for p in zip(*profiles) ]
        else:
            profiles = profiles[0]

        return profiles

    def getProfileTimes(self, prof_idxs=None):
        if prof_idxs is None:
            dates = self._dates
        else:
            dates = [ self._dates[i] for i in prof_idxs ]
        return dates

    def getStnId(self):
        return self._profiles.values()[0][0].location

if __name__ == "__main__":
    print "Creating bufkit decoder ..."
    bd = BufDecoder()
