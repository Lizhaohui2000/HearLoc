function [tau, cc] = my_gccphat(y, y_ref, interp)
    Fs = 48000;
    if nargin <= 2
        interp = 1;
    end
    n = 2*length(y);
    
    fft_y = fft(y, n);
    fft_y_ref = fft(y_ref, n);
    
    %%%%% FFT interpolation
    N_all = interp*n; N_pad = (N_all-n)/2;
    R = fft_y.*conj(fft_y_ref)./abs(fft_y.*conj(fft_y_ref));
    R_pad = fftshift([zeros(N_pad,1); fftshift(R); zeros(N_pad,1)]);
    cc = real(ifft(R_pad));
    max_shift = round(interp * n / 2);
    
    cc = [cc((max_shift+1):end); cc(1:(max_shift+1))];
%     cc = fftshift(cc);
    [~, ind] = max(real(cc));
    shift = ind - max_shift - 1;
    
    tau = shift / (interp * Fs);
    
end