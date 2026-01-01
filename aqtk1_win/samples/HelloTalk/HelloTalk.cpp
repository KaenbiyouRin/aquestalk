#include <stdio.h>
#include "AquesTalk.h"

main(int ac, char **av)
{
	AquesTalk_SetDevKey("xxxxxx");	// 開発ライセンスキーを指定 評価版の制限(ナ行マ行がヌになる)を外す
	AquesTalk_SetUsrKey("yyyyyy");	// 使用ライセンスキーを指定

	int size;
	unsigned char *wav = AquesTalk_Synthe("こんにちわ。", 100, &size);
	if(wav==0){
		fprintf(stderr, "ERR:%d\n",size);
		return -1;
	}

	FILE *fp=fopen("\\zzz.wav", "wb");
	fwrite(wav, 1, size, fp);
	fclose(fp);

	AquesTalk_FreeWave(wav);
 
	return 0;
}