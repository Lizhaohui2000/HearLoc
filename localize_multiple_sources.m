%%% sum all GCC 
addpath('.\utils\');
clear; 
Fs = 48000;
d_w = 0.4;
theta = 0;
d_a = 0.05;
c = 343;
minterp = 1;
M = 4;
D = (M-1)*d_a;
mrange = round(2*d_w/c*Fs+D/c*Fs+20);
roomdim = [8, 5, 3.5];
P_a = [4, d_w, 0.8]; P_arr = [];
for l = 1:M
    P_temp = P_a; P_temp(1) = P_temp(1) + d_a*(l-1);
    P_arr = [P_arr; P_temp];
end
P_arr(:,3) = P_arr(:,3)-P_a(3); 

mstep = 0.1;
max_H = 0;
x_range = 0:mstep:roomdim(1);
y_range = 0.5:mstep:roomdim(2);
z_range = 0:mstep:max_H;

%%%% load file
sourceFolder = '.\samples\multiple_sources_2D\';
filename = 'source1_10_30_source2_65_30.txt';
numbers = regexp(filename, '_\d+', 'match');
numbers = strrep(numbers, '_', '');
Source1 = str2double(numbers(1:2)); Source1 = Source1/10;
Source2 = str2double(numbers(3:4)); Source2 = Source2/10;
y_arr = load([sourceFolder,filename]);

N = 2*length(y_arr); 
max_shift_nointerp = length(y_arr);
max_shift = minterp*max_shift_nointerp;

%%%% generate delay arr
total_len = length(z_range)*length(x_range)*length(y_range);
delay_arr = zeros(total_len, 6*4); 
POS_arr = zeros(total_len, 3);
mtag = 1;

for t = 1:length(z_range)
    for m = 1:length(y_range)
        for n = 1:length(x_range)
            P_s = [x_range(n), y_range(m), z_range(t)];
            temp_idxarr_interp = []; 
            for k = 1:M-1
                for p = k+1:M
                    tau_arr = getAllDelays(P_s, P_arr(p,:), P_arr(k,:));
                    idx_arr_interp = round((tau_arr+max_shift_nointerp)*minterp+1);
                    temp_idxarr_interp = [temp_idxarr_interp, idx_arr_interp'];
                end
            end
            delay_arr(mtag, :) = temp_idxarr_interp;
            POS_arr(mtag, :) = P_s;
            mtag = mtag+1;
        end
    end
end

%%%% get CC spectrum
R_arr = [];
for k = 1:(size(y_arr, 2)-1)
    for l = (k+1):size(y_arr, 2)
        fft_yl = fft(y_arr(:,l), N);  
        fft_yk = fft(y_arr(:,k), N);
        R = fft_yl.*conj(fft_yk)./(abs(fft_yl.*conj(fft_yk)));
        R_arr = [R_arr, R];
    end
end
cc_nointerp = real(ifft(R_arr));
cc_nointerp_arr = [cc_nointerp((max_shift_nointerp+1):end, :); cc_nointerp(1:(max_shift_nointerp+1), :)];

% cc_nointerp2 = [cc_nointerp_arr((max_shift_nointerp+1):(end-1), :); cc_nointerp_arr(1:max_shift_nointerp, :)];

mround = 2;
for t = 1:mround
    N_pad = (minterp-1)*N/2;
    R_pad = fftshift([zeros(N_pad, size(R_arr,2)); fftshift(fft(cc_nointerp), 1); zeros(N_pad,size(R_arr,2))], 1);
    cc_pad = real(ifft(R_pad));
    cc_interp_arr = [cc_pad((max_shift+1):end, :); cc_pad(1:(max_shift+1), :)];
%     figure(); plot(cc_interp_arr(max_shift+minterp*(-100:100), 4))

    LSE_arr = zeros(total_len, 4);
    for m = 1:total_len
        for p = 1:4
            for k = 1:6
                LSE_arr(m, p) = LSE_arr(m, p) + sum(cc_interp_arr(delay_arr(m, p+4*(k-1)), k));
            end
        end
    end
    
    LSE_arr_norm = normalize(LSE_arr, 'range');
    LSE_arr_norm_sum = sum(LSE_arr_norm, 2);
    LSE_disp = reshape(LSE_arr_norm_sum, length(x_range), length(y_range))';
    LSE_disp = mat2gray(LSE_disp); 
    LSE_disp = LSE_disp.^4;

    [~, idx] = max(LSE_arr_norm_sum);
    P_s_est = POS_arr(idx,:);
    
    tag = 1;
    for k = 1:M-1
        for p = k+1:M
            tau_arr = getAllDelays(P_s_est, P_arr(p,:), P_arr(k,:));
            idx_arr = round(tau_arr+max_shift_nointerp+1);
            cc_nointerp_arr(idx_arr, tag) = 0;
            tag = tag + 1;
        end
    end

%     cc_nointerp = fftshift(cc_nointerp_arr, 1);
    cc_nointerp = [cc_nointerp_arr((max_shift_nointerp+1):(end-1), :); cc_nointerp_arr(1:max_shift_nointerp, :)];

    figure();
    set(gcf,'Units','centimeters','Position',[1.4 10 12 10]) 
    imagesc(x_range, y_range, LSE_disp);%LSE_disp
    set(gca, 'YDir', 'normal');
    title(['Round ', num2str(t)]);
    xlabel('X(m)')
    ylabel('Y(m)')
    set(gca,'FontSize',12,'FontName','Arial');
    hold on; plot(Source1(1), Source1(2), 'wo','MarkerSize',10,'LineWidth',1.5); 
    plot(Source2(1), Source2(2), 'wo','MarkerSize',10,'LineWidth',1.5); 
    hold off;
    text(Source1(1)+0.5, Source1(2)+0.5,'Source1', 'Color',[1,1,1],'FontWeight','bold','FontName','Arial','FontSize',12)
    text(Source2(1)-1.5, Source2(2)+0.5,'Source2', 'Color',[1,1,1],'FontWeight','bold','FontName','Arial','FontSize',12)

end
