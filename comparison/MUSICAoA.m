function P_arr = MUSICAoA(y_arr, dd)
    %%%%%%%%%%%%%%%
    %MUSIC AOA estimation with frequency normalization: https://github.com/LCAV/pyroomacoustics/blob/pypi-release/pyroomacoustics/doa/normmusic.py
    %%%%%%%%%%%%%%%
    c = 343; %% 声速
    N = length(y_arr); L = min(size(y_arr));
    Fs = 48000;
    K_est = 1;

    f_res = Fs/length(y_arr); 
    f_arr = 500:f_res:(5000-f_res);
    fft_y_rec = fft(y_arr);
    
    theta = (0:1:180)';
    P_arr = zeros(size(theta)); 

    for f_idx = 1:length(f_arr)
        f_temp_idx = round(f_arr(f_idx)*N/Fs+1);
        covMat = fft_y_rec(f_temp_idx,:)'*fft_y_rec(f_temp_idx,:);

        J = fliplr(eye(length(covMat),length(covMat)));
        covMat = (covMat + J*covMat.'*J)/2; 
        
        [U, D] = eig(covMat);
        [dD, idx] = sort(diag(D), 'descend');
        U = U(:, idx); 
        noiseSubspace = U(:, (K_est+1):end);
        P_arr_temp = zeros(size(theta)); %max_pow = 0; max_theta = -1;
        for m = 1:length(theta)
            tau_temp = -(0:(L-1))'*dd*cosd(theta(m))/c;
            a_vec = exp(1j*2*pi*f_arr(f_idx)*tau_temp);
            P_arr_temp(m) = 1/norm(noiseSubspace'*a_vec)^2;
        end
        P_arr = P_arr + P_arr_temp/max(P_arr_temp); % with frequency normalization. 
    end
end