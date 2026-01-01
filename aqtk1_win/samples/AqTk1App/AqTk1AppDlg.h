
// AqTk1AppDlg.h : ヘッダー ファイル
//

#pragma once


// CAqTk1AppDlg ダイアログ
class CAqTk1AppDlg : public CDialogEx
{
// コンストラクション
public:
	CAqTk1AppDlg(CWnd* pParent = nullptr);	// 標準コンストラクター

// ダイアログ データ
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_AQTK1APP_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV サポート


// 実装
protected:
	HICON m_hIcon;

	unsigned char* Synthe(int* pSize);
	unsigned char* m_wav;

	// 生成された、メッセージ割り当て関数
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	CString m_strKoe;
	afx_msg void OnBnClickedBtnPlay();
	afx_msg void OnBnClickedBtnStop();
	CSliderCtrl m_slider_speed;
	afx_msg void OnClose();
	int m_iSpeed;
};
