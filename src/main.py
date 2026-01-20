"""損益計算書BIツール エントリーポイント"""
from .app import Application


def main():
    """メイン関数"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
