#include <math.h>
#include <stdlib.h>


///////////////////////////////////////////////////////////////////////////
// This function does the actual correlation
///////////////////////////////////////////////////////////////////////////
void CCF(__int64_t *t1, __int64_t *t2, double *photons1, double *photons2, unsigned int nc, unsigned int nb,
        unsigned int np1, unsigned int np2, int *xdat, double *corrl)
{
    // t1, t2:              macrotime vectors
    // xdat:                correlation time bins (timeaxis)
    // np1, np2:            number of photons in each channel
    // photons1, photons2:  photon weights
    // nc:                  number of evenly spaced elements per block
    // nb:                  number of blocks of increasing spacing
    // corrl:               pointer to correlation output
    
    //Initializes some variables for for loops
    unsigned int i=0;
    unsigned int j=0;
    unsigned int k=0;
    unsigned int p=0;
    unsigned int im;
    
    //Initializes some parameters
    __int64_t maxmat;
    __int64_t index;
    __int64_t pw;
    __int64_t limit_l;
    __int64_t limit_r;
    
    //determine max macro time
    if (t1[np1-1]>t2[np2-1]) {maxmat=t1[np1-1];}
    else {maxmat=t2[np2-1];}
    
    // Goes through every block
    for (k=0;k<nb;k++)
    {
        // Determines spacing; used 2time spacing of one
        if (k==0) {pw=1;}
        else {pw=pow(2, k-1);};
        
        // p is the starting photon in second array
        p=0;
        
        // Goes through every photon in first array
        for (i=0;i<np1;i++) {
            //if (photons1[i]!=0)
            //{
                // Calculates minimal and maximal time for photons in second array
                limit_l= (__int64_t)(xdat[k*nc]/pw+t1[i]);
                limit_r= limit_l+nc;
                
                j=p;
                while ((j<np2) && (t2[j]<=limit_r))
                {
                    //if (photons2[j]!=0)
                    //{
                        if (k == 0) // Special Case for first round to include the zero time delay bin
                        {
                            // If correlation time is positiv OR equal
                            if (t2[j]>=limit_l)
                            {
                                // Calculates time between two photons
                                index=t2[j]-limit_l+(__int64_t)(k*nc);
                                // Adds one to correlation at the appropriate timelag
                                corrl[index]+=(double) (photons1[i]*photons2[j]);
                            }
                            // Increases starting photon in second array, to save time
                            else {p++;}
                        }
                        else
                        {
                            // If correlation time is positiv
                            if (t2[j]>limit_l)
                            {
                                // Calculates time between two photons
                                index=t2[j]-limit_l+(__int64_t)(k*nc);
                                // Adds one to correlation at the appropriate timelag
                                corrl[index]+=(double) (photons1[i]*photons2[j]);
                            }
                            // Increases starting photon in second array, to save time
                            else {p++;}
                        }
                    //}
                    j++;
                };
            //};
        };
        
        //After second iteration;
        if (k>0)
        {
            // Bitwise shift right => Corresponds to dividing by 2 and rounding down
            // If two photons are in the same time bin, sums intensities and sets one to 0 to save calculation time
            for(im=0;im<np1;im++) {t1[im]=t1[im]>>1;};
            for(im=1;im<np1;im++)
            {
                if (t1[im]==t1[im-1])
                {photons1[im]+=photons1[im-1]; photons1[im-1]=0;};
            };
            for(im=0;im<np2;im++) {t2[im]=t2[im]>>1;};
            for(im=1;im<np2;im++)
            {
                if (t2[im]==t2[im-1])
                {photons2[im]+=photons2[im-1]; photons2[im-1]=0;};
            };
        };
        
        //
        j=0;
        for (i=0; i<np1; i++)
        {
            if (photons1[i] != 0)
            {
                photons1[j] = photons1[i];
                t1[j] = t1[i];
                j++;
            }
        }        
        np1=j;
        
        j=0;
        for (i=0; i<np2; i++)
        {
            if (photons2[i] != 0)
            {
                photons2[j] = photons2[i];
                t2[j] = t2[i];
                j++;
            }
        }
        np2=j;
    };
    
    return;
};
