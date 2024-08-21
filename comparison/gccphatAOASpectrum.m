function AOAspectrum = gccphatAOASpectrum(y_arr, d_a)

    Fs = 48000;
    c = 343; 
    L = min(size(y_arr));
    minterp = 9;

    tau_l = @(theta, l) -(l-1)*d_a*cos(theta)/c;
    max_lag = ceil((L-1)*d_a/c*Fs)*minterp;
    
    theta_range = (0:1:180)';
    AOAspectrum = zeros(size(theta_range));
    for m = 2:L
        [~, R] = my_gccphat(y_arr(:,m), y_arr(:,1), minterp);
        half_len = round((length(R)+1)/2);
        for n = 1:length(theta_range)
            mdelay = round(tau_l(theta_range(n)/180*pi, m)*Fs*minterp);
            AOAspectrum(n) = AOAspectrum(n)+R(half_len+mdelay);
        end
    end

end