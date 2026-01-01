
// AqTk1AppDlg.cpp : 実装ファイル
//

#include "pch.h"
#include "framework.h"
#include "AqTk1App.h"
#include "AqTk1AppDlg.h"
#include "afxdialogex.h"

#include "AquesTalk.h"
#include <mmsystem.h>
#pragma comment(lib, "winmm.lib")	// PlaySound

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// CAqTk1AppDlg ダイアログ



CAqTk1AppDlg::CAqTk1AppDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_AQTK1APP_DIALOG, pParent)
	, m_strKoe(_T("ばくおんが、ぎんせ'かいの/こーげんに/ひろがる。"))
	, m_wav(0)
	, m_iSpeed(0)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CAqTk1AppDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_EDIT1, m_strKoe);
	DDX_Slider(pDX, IDC_SPEED, m_iSpeed);
	DDV_MinMaxInt(pDX, m_iSpeed, 50, 200);
}

BEGIN_MESSAGE_MAP(CAqTk1AppDlg, CDialogEx)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BTN_PLAY, &CAqTk1AppDlg::OnBnClickedBtnPlay)
	ON_BN_CLICKED(IDC_BTN_STOP, &CAqTk1AppDlg::OnBnClickedBtnStop)
	ON_WM_CLOSE()
//	ON_WM_HSCROLL()
END_MESSAGE_MAP()


// CAqTk1AppDlg メッセージ ハンドラー

BOOL CAqTk1AppDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// このダイアログのアイコンを設定します。アプリケーションのメイン ウィンドウがダイアログでない場合、
	//  Framework は、この設定を自動的に行います。
	SetIcon(m_hIcon, TRUE);			// 大きいアイコンの設定
	SetIcon(m_hIcon, FALSE);		// 小さいアイコンの設定

	// TODO: 初期化をここに追加します。
	m_iSpeed = 100;
	((CSliderCtrl*)GetDlgItem(IDC_SPEED))->SetRange(50, 200);
	((CSliderCtrl*)GetDlgItem(IDC_SPEED))->SetPageSize(10);
	((CSliderCtrl*)GetDlgItem(IDC_SPEED))->SetPos(m_iSpeed);

	AquesTalk_SetDevKey("xxxxxx");	// 開発ライセンスキーを指定 評価版の制限(ナ行マ行がヌになる)を外す
	AquesTalk_SetUsrKey("yyyyyy");	// 使用ライセンスキーを指定

	UpdateData(FALSE);
	return TRUE;  // フォーカスをコントロールに設定した場合を除き、TRUE を返します。
}

// ダイアログに最小化ボタンを追加する場合、アイコンを描画するための
//  下のコードが必要です。ドキュメント/ビュー モデルを使う MFC アプリケーションの場合、
//  これは、Framework によって自動的に設定されます。

void CAqTk1AppDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 描画のデバイス コンテキスト

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// クライアントの四角形領域内の中央
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// アイコンの描画
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

// ユーザーが最小化したウィンドウをドラッグしているときに表示するカーソルを取得するために、
//  システムがこの関数を呼び出します。
HCURSOR CAqTk1AppDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}



void CAqTk1AppDlg::OnBnClickedBtnPlay()
{
	if (m_wav)	AquesTalk_FreeWave(m_wav);
	int size;
	m_wav = Synthe(&size);
	// DA
	if (m_wav) {
		// play sound
		PlaySound((LPCSTR)NULL, NULL, SND_MEMORY);	// STOP
		PlaySound((LPCSTR)m_wav, NULL, SND_MEMORY | SND_ASYNC);	// play
	}
}


void CAqTk1AppDlg::OnBnClickedBtnStop()
{
	PlaySound((LPCSTR)NULL, NULL, SND_MEMORY);	// STOP
}



void CAqTk1AppDlg::OnClose()
{
	if (m_wav)	AquesTalk_FreeWave(m_wav);
	UpdateData(TRUE);

	CDialogEx::OnClose();
}


unsigned char* CAqTk1AppDlg::Synthe(int* pSize)
{
	UpdateData(TRUE);
	CString koe = m_strKoe;
	// 改行コードを削除
	koe.Replace("\r", "");
	koe.Replace("\n", "");
	if (koe == "") {
		AfxMessageBox("ERR:音声記号列が指定されていない");
		return 0;
	}
	// 音声合成
	int size;
	unsigned char* wav = AquesTalk_Synthe(koe, m_iSpeed, &size); // AquesTalk_Synthe()
	if (wav == 0) {
		CString sss;
		if (size == 105)		sss.Format("ERR: 音声記号列に未定義の読み記号が指定された。(%d)", size);
		else if (size == 106 || size == 107 || size == 108)	sss.Format("ERR: 音声記号列のタグの指定が正しくない。(%d)", size);
		else if (200 <= size && size <= 204)	sss.Format("ERR: 音声記号列が長すぎる。(%d)", size);
		else if (900 <= size && size <= 999)	sss.Format("ERR: Profileの指定エラー(%d)", size);
		else						sss.Format("ERR:音声記号列が正しくない？(%d)", size);
		AfxMessageBox(sss);
		return 0;
	}
	* pSize = size;
	return wav;
}

