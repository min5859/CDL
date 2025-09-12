import streamlit as st
import pandas as pd

# pickle 파일로부터 DataFrame 불러오기 함수
def load_data(file_path):
    try:
        df = pd.read_pickle(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading the pickle file: {e}")
        return None

# 메인 함수
def main():
    st.title("Excel-like Viewer for Pickle Data")

    # 파일 업로드 위젯
    uploaded_file = st.file_uploader(".\function_map\sample_dataframe.pkl", type=["pkl"])

    if uploaded_file is not None:
        # 파일 읽기
        df = load_data(uploaded_file)

        if df is not None:
            # 데이터 테이블 표시
            st.dataframe(df)  # Streamlit에서 테이블을 엑셀 스타일로 표시

            # 데이터 다운로드 옵션 제공 (엑셀 형식으로 다운로드 가능)
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            # CSV로 다운로드 버튼
            csv = convert_df_to_csv(df)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='data.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
