#!/bin/bash
sed -i 's;<OffSetNLL>False</OffSetNLL>;<OffSetNLL>False</OffSetNLL>\n<UseGSLNumericalIntegration>True</UseGSLNumericalIntegration>\n<FixedIntegrationPoints>100000</FixedIntegrationPoints>;' $1
sed -i 's;<Source>File</Source>;<Source>Foam</Source>;' $1
sed -i 's;<FileName>toy.root</FileName>;;' $1
sed -i 's;<NumberEvents>43800</NumberEvents>;<NumberEvents>4380000</NumberEvents>;' $1
