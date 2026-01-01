
// AqTk1App.h : PROJECT_NAME アプリケーションのメイン ヘッダー ファイルです
//

#pragma once

#ifndef __AFXWIN_H__
	#error "PCH に対してこのファイルをインクルードする前に 'pch.h' をインクルードしてください"
#endif

#include "resource.h"		// メイン シンボル


// CAqTk1AppApp:
// このクラスの実装については、AqTk1App.cpp を参照してください
//

class CAqTk1AppApp : public CWinApp
{
public:
	CAqTk1AppApp();

// オーバーライド
public:
	virtual BOOL InitInstance();

// 実装

	DECLARE_MESSAGE_MAP()
};

extern CAqTk1AppApp theApp;
