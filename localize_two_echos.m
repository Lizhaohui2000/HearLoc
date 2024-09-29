clear; 
addpath('.\utils\');

Fs_org = 48000; 
Fs = 48000; 
d_w1 = 0.3;
d_w2 = 0.3;
d_w_max = sqrt(d_w1^2 + d_w2^2);
theta = 0;
d_a = 0.05;
c = 343;
minterp = 9;
M = 4;
D = (M-1)*d_a;
mrange = round(2*d_w_max/c*Fs+D/c*Fs+20);
topk = ceil(D*Fs/c*minterp*0.2);
roomdim = [8, 5, 3.2];
P_a = [d_w2, d_w1, 0.8]; P_arr = [];
for l = 1:M
    P_temp = P_a; P_temp(1) = P_temp(1) + d_a*(l-1);
    P_arr = [P_arr; P_temp];
end
P_arr(:,3) = P_arr(:,3)-0.8; 
dim  =  2; %dim-3;

foldname = '.\samples\two_walls_2D\';
file_list = dir(fullfile(foldname, '*.txt'));
data_amount = length(file_list);

mstep = 0.1;
x_range = 0:mstep:roomdim(1);
y_range = 0.5:mstep:roomdim(2);
if dim == 2
    max_H = 0;
elseif dim == 3
    max_H = 1;
end
z_range = 0:mstep:max_H;

%%%% generate delay arr
total_len = length(z_range)*length(x_range)*length(y_range);
Mic_comb_num = M*(M-1)/2; 
model_num = 3; corr_num = model_num^2; 
delay_arr = zeros(total_len, round(Mic_comb_num*corr_num));

POS_arr = zeros(total_len, 3);
P_GT_arr = zeros(data_amount, 3);
P_ET_arr = zeros(data_amount, 3);
mtag = 1;

for t = 1:length(z_range)
    for m = 1:length(y_range)
        for n = 1:length(x_range)
            P_s = [x_range(n), y_range(m), z_range(t)];
            temp_idxarr = [];
            for k = 1:M-1
                for p = k+1:M
                    tau_arr = getAllDelays_twoECHOS(P_s, P_arr(p,:), P_arr(k,:), Fs);
%                     tau_arr = getAllDelays(P_s, P_arr(p,:), P_arr(k,:), Fs);
                    idx_arr = round((tau_arr+mrange)*minterp+1);
                    temp_idxarr = [temp_idxarr, idx_arr'];
                end
            end
            delay_arr(mtag, :) = temp_idxarr;
            POS_arr(mtag, :) = P_s;
            mtag = mtag+1;
        end
    end
end

file_list = dir(fullfile(foldname, '*.txt'));
for b = 1:data_amount %10%
    %%%% load file
    filename = file_list(b).name;
    if dim == 2
        pattern = '_(\d+)_(\d+)\.txt$';
        matches = regexp(filename, pattern, 'tokens');
        P_GT_arr(b, :) = [str2double(matches{1}{1}), str2double(matches{1}{2}), 0]/10;
    elseif dim  == 3
        pattern = '_(\d+)_(\d+)_(\d+)\.txt$';
        matches = regexp(filename, pattern, 'tokens');
        P_GT_arr(b, :) = [str2double(matches{1}{1}), str2double(matches{1}{2}), str2double(matches{1}{3})]/10;
    end
    filename_txt = fullfile(foldname, file_list(b).name);
    y_arr = load(filename_txt);

    %%%% get CC spectrum
    R_arr = zeros(2*mrange*minterp+1, Mic_comb_num); mflag = 1;
    for k = 1:(size(y_arr, 2)-1)
        for l = (k+1):size(y_arr, 2)
            [~, R] = my_gccphat(y_arr(:,l), y_arr(:,k), minterp);
            R = R((length(y_arr)*minterp+(-mrange*minterp:mrange*minterp)+1),:);
            R_arr(:, mflag) = R; mflag = mflag + 1;
        end
    end

    %%%% prune search space
    LSE_arr = zeros(total_len, corr_num);
    LOS_AOA_range = round(D/c*Fs)*minterp;
    [~, topk_idxarr] = maxk(R_arr(mrange*minterp+1+(-LOS_AOA_range:LOS_AOA_range), 3), topk);
    topk_idxarr = mrange*minterp+1+topk_idxarr-LOS_AOA_range-1;
    for m = 1:total_len
        if ismember(delay_arr(m, 2*corr_num+1), topk_idxarr) 
            for p = 1:corr_num
                for k = 1:Mic_comb_num
                    LSE_arr(m, p) = LSE_arr(m, p) + R_arr(delay_arr(m, p+corr_num*(k-1)), k);
                end
            end
        end
    end
    LSE_arr = normalize(LSE_arr, 'range');
    LSE_arr = sum(LSE_arr, 2);
    [~,idx] = max(LSE_arr);
    P_ET_arr(b, :) = POS_arr(idx, :);
end

error_arr = vecnorm(P_ET_arr-P_GT_arr, 2, 2);
median(error_arr)

