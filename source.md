Đề bài: Tam giác $ABC$ nhọn, không cân ($AB < AC$) ngoại tiếp đường tròn $(I)$; các tiếp điểm của $(I)$ với $BC, CA, AB$ lần lượt là $D, E, F$. Gọi $K, L$ là chân các đường vuông góc hạ từ $B, C$ lên đường thẳng qua $I$ song song với $EF$.

\textbf{1.} Chứng minh $DK \parallel IC$.


\textbf{2.} Chứng minh $KF, EL$ cắt nhau trên $(I)$.


\textbf{3.} Gọi $M, N$ lần lượt là giao điểm khác $D$ của $DK, DL$ với $(I)$; $MN$ cắt $BC$ tại $P$; dựng đường kính $DS$ của $(I)$. Chứng minh $PI \perp AS$.



Hình vẽ: \begin{center}

\begin{tikzpicture}[scale=1.3] % Phóng to một chút vì hình có nhiều chi tiết

\tkzDefPoint(0,4.5){A}

\tkzDefPoint(-2.5,0){B}

\tkzDefPoint(6,0){C}

\tkzDefTriangleCenterin \tkzGetPoint{I}

\tkzDefPointByprojection=onto B--C \tkzGetPoint{D}

\tkzDefPointByprojection=onto A--C \tkzGetPoint{E}

\tkzDefPointByprojection=onto A--B \tkzGetPoint{F}

\tkzDefLineparallel=through I \tkzGetPoint{i_par}

\tkzDefPointByprojection=onto I--i_par \tkzGetPoint{K}

\tkzDefPointByprojection=onto I--i_par \tkzGetPoint{L}

% Các điểm M, N (đối xứng của E, F qua I)

\tkzDefPointBy[symmetry=center I](E) \tkzGetPoint{M}

\tkzDefPointBy[symmetry=center I](F) \tkzGetPoint{N}


% Giao điểm P của MN và BC

\tkzInterLL(M,N)(B,C) \tkzGetPoint{P}


% Đường kính DS

\tkzDefPointBy[symmetry=center I](D) \tkzGetPoint{S}


% Giao điểm X, Y

\tkzInterLL(A,I)(E,F) \tkzGetPoint{X}

\tkzInterLL(A,I)(M,N) \tkzGetPoint{Y}


% Vẽ hình

\tkzDrawPolygon[thick, blue!80!black](A,B,C)

\tkzDrawCircle[thick, green!60!black](I,D)

\tkzDrawLine[thick, orange](K,L)


\tkzDrawSegments[thick](E,F M,N B,K C,L D,K D,L P,M D,S A,I)

\tkzDrawSegments[thick, red](A,S P,I) % Cặp đường thẳng cần chứng minh vuông góc

\tkzDrawSegments[thick, dashed](M,E N,F)


\tkzDrawPoints[fill=black, size=3](A,B,C,I,D,E,F,K,L,M,N,P,S,Y)

\tkzLabelPoints[above](A,S)

\tkzLabelPoints[below](D,P)

\tkzLabelPoints[left](B,F,K)

\tkzLabelPoints[right](C,L,E)

\tkzLabelPoints[below left](M)

\tkzLabelPoints[below right](N)

\tkzLabelPoints[above right](I,Y)

\end{tikzpicture}

\end{center}



Lời giải:

\textbf{1.} Ta có $EF \parallel KI$ nên $\widehat{KIF} = \widehat{IFE} = \widehat{IEF}$, suy ra

$$ \widehat{KIB} = \widehat{BIF} - \widehat{KIF} = \widehat{FED} - \widehat{IEF} = \widehat{IED} = \widehat{ICD}. $$

Mặt khác do $\widehat{BKI} = \widehat{BDI} = 90^\circ$ nên tứ giác $BKID$ nội tiếp, dẫn tới

$$ \widehat{BDK} = \widehat{BIK} = \widehat{ICD}, $$

kéo theo $DK \parallel IC$.

\textbf{2.}      Do $\widehat{BFI} = 90^\circ$ nên $F$ thuộc đường tròn đường kính $BI$, suy ra 5 điểm $B, K, F, I, D$ đồng viên. Gọi giao điểm của $KF$ với $(I)$ là $J$, ta có

$$ \widehat{JED} = 180^\circ - \widehat{IFD} = \widehat{KFD} = \widehat{KID}. $$

Tương tự, $I, E, L, D, C$ đồng viên nên

$$ \widehat{DEL} = 180^\circ - \widehat{DCL} = \widehat{DIL}. $$

Dẫn tới

$$ \widehat{JED} + \widehat{DEL} = \widehat{KID} + \widehat{DIL} = 180^\circ, $$

suy ra $J, E, L$ thẳng hàng, tức $KF, EL$ cắt nhau trên $(I)$.

\textbf{3.}    Do $KD \parallel IC$ mà $IC \perp ED$ nên $KD \perp ED$, kéo theo $E, I, M$ thẳng hàng. Tương tự $F, I, N$ thẳng hàng, suy ra $MNEF$ là hình chữ nhật. Gọi $X, Y$ lần lượt là giao điểm của $AI$ với $EF, MN$, thì $IX = IY$. \

Hơn nữa,

$$ IX \cdot IA = IE^2 = IS \cdot ID, $$

nên $\dfrac{IS}{IA} = \dfrac{IY}{ID}$. Kết hợp với $\widehat{AIS} = \widehat{DIY}$, ta được $\Delta AIS \sim \Delta DIY$ (c.g.c). Do đó $\widehat{SAI} = \widehat{IDY}$. \

Mặt khác, $IA \perp MN$ nên $\widehat{IYP} = \widehat{IDP} = 90^\circ$, suy ra tứ giác $PDYI$ nội tiếp đường tròn đường kính $PI$. Do đó

$$ \widehat{IPY} = \widehat{IDY} = \widehat{IAS}, $$

suy ra $AS \perp PI$.