function aoa_spec = DSB(y_arr, d_a)
    c = 343; Fs = 48e3;
    N = max(size(y_arr,1 )); M = min(size(y_arr));
    thete_arr = (0:180)';
    aoa_spec = zeros(size(thete_arr));
    for k = 1:length(thete_arr)
        DSB_y = y_arr(:, 1);
        for m = 2:M
            tau = d_a/c*(m-1)*cos(thete_arr(k)/180*pi);
            DSB_y = DSB_y+delayseq(y_arr(:, m), tau, Fs);
        end
        aoa_spec(k)= sum(abs(DSB_y));
    end
end