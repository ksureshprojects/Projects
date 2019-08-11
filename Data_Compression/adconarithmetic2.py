from math import floor, ceil
from sys import stdout as so
from bisect import bisect

def enfreq(t):
    p = [[[(i, t[j][k][i]/t[j][k][128]) for i in range(128)] for k in range(129)] for j in range(129)]
    f = [[[] for k in range(129)] for j in range(129)]
    for j in range(len(p)):
        for k in range(len(p[j])):
            if len(p[j][k]) > 0:
                f[j][k].append((p[j][k][0][0],0)) #First conditional cumalative probability term (symbol, value)
                for i in range(1,len(p[j][k])):
                    f[j][k].append((p[j][k][i][0],f[j][k][-1][1] + p[j][k][i-1][1]))
                    
                f[j][k] = dict(f[j][k])

    p = [[dict(k) if len(k) > 0 else k for k in p[j]] for j in range(len(p))]
    
    return p,f

def defreq(t):
    # Compute cumulative probability as in Shannon-Fano
    p = [[[(i, t[j][k][i]/t[j][k][128]) for i in range(128)] for k in range(129)] for j in range(129)]
    f = [[[] for k in range(129)] for j in range(129)]
    for j in range(len(p)):
        for k in range(len(p[j])):
            if len(p[j][k]) > 0:
                #First conditional cumalative probability term (symbol, value)
                f[j][k].append([p[j][k][0][0]])
                f[j][k].append([0])
                for i in range(1,len(p[j][k])):
                    f[j][k][0].append(p[j][k][i][0])
                    f[j][k][1].append(f[j][k][1][-1] + p[j][k][i-1][1])
            
    p = [[dict(k) if len(k) > 0 else k for k in p[j]] for j in range(len(p))]
    
    return p,f

def enupdate(p,f,t,c2,c1):
    p[c2][c1] = [(i, t[c2][c1][i]/t[c2][c1][128]) for i in range(128)]
    f[c2][c1] = []
    f[c2][c1].append((p[c2][c1][0][0],0)) #First conditional cumalative probability term (symbol, value)
    for i in range(1,len(p[c2][c1])):
        f[c2][c1].append((p[c2][c1][i][0],f[c2][c1][-1][1] + p[c2][c1][i-1][1]))
        
    f[c2][c1] = dict(f[c2][c1])
    p[c2][c1] = dict(p[c2][c1])
    return p,f

def deupdate(p,f,t,c2,c1):
    p[c2][c1] = [(i, t[c2][c1][i]/t[c2][c1][128]) for i in range(128)]
    f[c2][c1] = []
    f[c2][c1].append([p[c2][c1][0][0]])  #(Symbol)
    f[c2][c1].append([0]) #(Value)
    for i in range(1,len(p[c2][c1])):
        f[c2][c1][0].append(p[c2][c1][i][0])
        f[c2][c1][1].append(f[c2][c1][1][-1] + p[c2][c1][i-1][1])
    p[c2][c1] = dict(p[c2][c1])
    return p,f

def encode(x, b): #Text = x, Frequency Table Bias = b

    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter
    #Initialise Frequency Table
    t = [[[b for i in range(129)] for k in range(129)] for j in range(129)] #bias probability table context 2
    for j in range(129): 
        for k in range(129):
            t[j][k][128] = sum(t[j][k]) - t[j][k][128] #Laplacian Bias

    p,f = enfreq(t)

    
    y = [] # initialise output list
    lo,hi = 0,one # initialise lo and hi to be [0,1.0)
    straddle = 0 # initialise the straddle counter to 0

    
    for k in range(len(x)): # for every symbol

        # arithmetic coding is slower than vl_encode, so we display a "progress bar"
        # to let the user know that we are processing the file and haven't crashed...
        if k % 100 == 0:
            so.write('Arithmetic encoded %d%%    \r' % int(floor(k/len(x)*100)))
            so.flush()

        # 1) calculate the interval range to be the difference between hi and lo and 
        # add 1 to the difference. The added 1 is necessary to avoid rounding issues
        lohi_range = hi - lo + 1

        # 2) Choose correct conditional density
        if k == 0:
            f_sub = f[128][128]
            p_sub = p[128][128]
        elif k == 1:
            f_sub = f[128][x[k-1]]
            p_sub = p[128][x[k-1]]
        else:
            f_sub = f[x[k-2]][x[k-1]] #f_sub assigned dictionary
            p_sub = p[x[k-2]][x[k-1]] #p_sub assigned dictionary

        # 3) narrow the interval end-points [lo,hi) to the new range [f,f+p]
        # within the old interval [lo,hi], being careful to round 'innwards' so
        # the code remains prefix-free (you want to use the functions ceil and
        # floor). This will require two instructions. Note that we start computing
        # the new 'lo', then compute the new 'hi' using the scaled probability as
        # the offset from the new 'lo' to the new 'hi'

        lo = lo + int(ceil(f_sub[x[k]] * lohi_range))
        hi = lo + int(floor(p_sub[x[k]] * lohi_range))

        if (lo == hi):
            raise NameError('Zero interval!')

        # Now we need to re-scale the interval if its end-points have bits in common,
        # and output the corresponding bits where appropriate. We will do this with an
        # infinite loop, that will break when none of the conditions for output / straddle
        # are fulfilled
        while True:
            if hi < half: # if lo < hi < 1/2
                # stretch the interval by 2 and output a 0 followed by 'straddle' ones (if any)
                # and zero the straddle after that. In fact, HOLD OFF on doing the stretching:
                # we will do the stretching at the end of the if statement
                #... # append a zero to the output list y
                y.append(0)
                #... # extend by a sequence of 'straddle' ones
                y.extend([1]*straddle)
                #... # zero the straddle counter
                straddle = 0
        
            elif lo >= half: # if hi > lo >= 1/2
                # stretch the interval by 2 and substract 1, and output a 1 followed by 'straddle'
                # zeros (if any) and zero straddle after that. Again, HOLD OFF on doing the stretching
                # as this will be done after the if statement, but note that 2*interval - 1 is equivalent
                # to 2*(interval - 1/2), so for now just substract 1/2 from the interval upper and lower
                # bound (and don't forget that when we say "1/2" we mean the integer "half" we defined
                # above: this is an integer arithmetic implementation!
                #... # append a 1 to the output list y
                y.append(1)
                #... # extend 'straddle' zeros
                y.extend([0]*straddle)
                #... # reset the straddle counter
                straddle = 0
                #...
                #... # substract half from lo and hi
                lo = lo - half
                hi = hi - half
         
            elif lo >= quarter and hi < threequarters: # if 1/4 < lo < hi < 3/4
                # we can increment the straddle counter and stretch the interval around
                # the half way point. This can be impemented again as 2*(interval - 1/4),
                # and as we will stretch by 2 after the if statement all that needs doing
                # for now is to subtract 1/4 from the upper and lower bound
                #... # increment straddle
                straddle += 1
                #...
                #... # subtract 'quarter' from lo and hi
                lo = lo - quarter
                hi = hi - quarter

            else:
                break # we break the infinite loop if the interval has reached an un-stretchable state
            # now we can stretch the interval (for all 3 conditions above) by multiplying by 2
            #... # multiply lo by 2
            lo = 2*lo
            #... # multiply hi by 2 and add 1 (I DON'T KNOW WHY +1 IS NECESSARY BUT IT IS. THIS IS MAGIC.
            hi = hi*2 + 1
                # A BOX OF CHOCOLATES FOR ANYONE WHO GIVES ME A WELL ARGUED REASON FOR THIS... It seems
                # to solve a minor precision problem.)

        # Updating freuqency table
        if k == 0:
            t[128][128][x[k]] += 1
            t[128][128][128] += 1
            p,f = enupdate(p,f,t,128,128)
        elif k == 1:
            t[128][x[k-1]][x[k]] += 1
            t[128][x[k-1]][128] += 1
            p,f = enupdate(p,f,t,128,x[k-1])
        else:
            t[x[k-2]][x[k-1]][x[k]] += 1
            t[x[k-2]][x[k-1]][128] += 1
            p,f = enupdate(p,f,t,x[k-2],x[k-1])

        # Updating probabilities and cumalative probabilities
        

        # if (int(t[128]) % scale[0]) == 0:
        #     t = [t[i]*scale[1] for i in range(len(t))]
        #     print('bob')
        
        # else:
        #     if t[128] < num:
        #         t[x[k]] += 1
        #         t[128] += 1
        #         # if (int(t[128]) % scale[0]) == 0:
        #         #     t = [t[i]*scale[1] for i in range(len(t))]
        #         p,f = freq(t,0)



    # termination bits
    # after processing all input symbols, flush any bits still in the 'straddle' pipeline
    straddle += 1 # adding 1 to straddle for "good measure" (ensures prefix-freeness)
    if lo < quarter: # the position of lo determines the dyadic interval that fits
        #... # output a zero followed by "straddle" ones
        y.append(0)
        #...
        y.extend([1]*straddle)

    else:
        #... # output a 1 followed by "straddle" zeros
        y.append(1)
        y.extend([0]*straddle)

    return(y)

def decode(y,b,n): #Coded Text = y, bias = b, number of characters in original text = n
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter

    #Initialise Frequency Table
    t = [[[b for i in range(129)] for k in range(129)] for j in range(129)] #bias probability table context 2
    for j in range(129): 
        for k in range(129):
            t[j][k][128] = sum(t[j][k]) - t[j][k][128] #Laplacian Bias


    p,f = defreq(t)
    

    y.extend(precision*[0]) # dummy zeros to prevent index out of bound errors
    x = n*[0] # initialise all zeros 

    # initialise by taking first 'precision' bits from y and converting to a number
    value = int(''.join(str(a) for a in y[0:precision]), 2) 
    position = precision # position where currently reading y
    lo,hi = 0,one

    for k in range(n):
        if k % 100 == 0:
            so.write('Arithmetic decoded %d%%    \r' % int(floor(k/n*100)))
            so.flush()


        lohi_range = hi - lo + 1
        # This is an essential subtelty: the slowest part of the decoder is figuring out
        # which symbol lands us in an interval that contains the encoded binary string.
        # This can be extremely wasteful (o(n) where n is the alphabet size) if you proceed
        # by simple looping and comparing. Here we use Python's "bisect" function that
        # implements a binary search and is 100 times more efficient. Try
        # for a = [a for a in f if f[a]<(value-lo)/lohi_range)][-1] for a MUCH slower solution.

        # 2) Choose correct conditional density
        if k == 0:
            f_sub = f[128][128][1]
            f_value = f[128][128][0]
            p_sub = p[128][128]
        elif k == 1:
            f_sub = f[128][x[k-1]][1]
            f_value = f[128][x[k-1]][0]
            p_sub = p[128][x[k-1]]
        else:
            f_sub = f[x[k-2]][x[k-1]][1]
            f_value = f[x[k-2]][x[k-1]][0]
            p_sub = p[x[k-2]][x[k-1]]
        # This is an essential subtelty: the slowest part of the decoder is figuring out
        # which symbol lands us in an interval that contains the encoded binary string.
        # This can be extremely wasteful (o(n) where n is the alphabet size) if you proceed
        # by simple looping and comparing. Here we use Python's "bisect" function that
        # implements a binary search and is 100 times more efficient. Try
        # for a = [a for a in f if f[a]<(value-lo)/lohi_range)][-1] for a MUCH slower solution.
        
        a = bisect(f_sub, (value-lo)/lohi_range) - 1
        x[k] = f_value[a] # output alphabet[a]
        
        lo = lo + int(ceil(f_sub[a]*lohi_range))
        hi = lo + int(floor(p_sub[x[k]]*lohi_range))

        if (lo == hi):
            raise NameError('Zero interval!')

        while True:
            if hi < half:
                # do nothing
                pass
            elif lo >= half:
                lo = lo - half
                hi = hi - half
                value = value - half
            elif lo >= quarter and hi < threequarters:
                lo = lo - quarter
                hi = hi - quarter
                value = value - quarter
            else:
                break
            lo = 2*lo
            hi = 2*hi + 1
            value = 2*value + y[position]
            position += 1
            if position == len(y):
                raise NameError('Unable to decompress')
        
        if k == 0:
            t[128][128][x[k]] += 1
            t[128][128][128] += 1
            p,f = deupdate(p,f,t,128,128)
        elif k == 1:
            t[128][x[k-1]][x[k]] += 1
            t[128][x[k-1]][128] += 1
            p,f = deupdate(p,f,t,128,x[k-1])
        else:
            t[x[k-2]][x[k-1]][x[k]] += 1
            t[x[k-2]][x[k-1]][128] += 1
            p,f = deupdate(p,f,t,x[k-2],x[k-1])

        # Updating probabilities and cumalative probabilities

    return(x)
    
