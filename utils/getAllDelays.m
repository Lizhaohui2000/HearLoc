function tau_arr = getAllDelays(P_s, P_2, P_1, Fs, c)
    if nargin<=3
        Fs = 48000;
    end
    if nargin<=4
        c = 343;
    end

    P_2v = P_2; P_2v(2) = -P_2v(2); 
    P_1v = P_1; P_1v(2) = -P_1v(2);

    tau_arr = [getTau(P_s, P_2, P_1); getTau(P_s, P_2v, P_1v); getTau(P_s, P_2v, P_1); getTau(P_s, P_2, P_1v)]*Fs;

    function ret = getTau(P_s, P_2, P_1)
        ret = (norm((P_s-P_2))-norm((P_s-P_1)))/c;
    end

end