import pandas as pd
import subprocess

def generate_submission_file_based_on_prediction(result, source_file_path="data/sample_submission.csv"):
    df = pd.read_csv(
        filepath_or_buffer=source_file_path,
        sep=",",
    ).set_index("ID")
    print(f"Entry: {df.shape}.")
    merge_df = pd.merge(
        left=df,
        right=result,
        how="left",
        on=["ID"],
    )
    print(f"Output: {merge_df.shape}.")
    if df.shape[0] != merge_df.shape[0]:
        raise ValueError(f"Should be same size.")
    merge_df = merge_df[["ID", "topredict"]]
    merge_df["topredict"] = merge_df["topredict"].fillna(0.0)
    merge_df["topredict"] = merge_df["topredict"] / 6
    # merge_df[merge_df["topredict"] < 0.0]["topredict"] = 0.0
    merge_df = merge_df.rename(columns={"topredict": "item_cnt_month"})
    merge_df.to_csv("data/my_submission.csv", sep=",", index=False)


def generate_random_submission(source_file_path="data/sample_submission.csv"):
    df = pd.read_csv(
        filepath_or_buffer=source_file_path,
        sep=",",
    )
    df["item_cnt_month"] = df["item_cnt_month"].apply(lambda x: random.uniform(0.2, 1.2))
    print(f"File data/my_submission.csv successfully generated.\n")
    df.to_csv("data/my_submission.csv", sep=",", index=False)


def submit_submission(submission_file="data/my_submission.csv"):
    with open("kaggle.json") as credential:
        json_credential = json.loads(credential.read())
        os.environ["KAGGLE_USERNAME"] = json_credential["username"]
        os.environ["KAGGLE_KEY"] = json_credential["key"]
    result = subprocess.check_output(
        [
            "kaggle",
            "competitions",
            "submit",
            "competitive-data-science-predict-future-sales",
            "-f",
            submission_file,
            "-m",
            f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: New submission",
        ]
    ).decode("utf-8")
    print(result)


def get_latest_score(team_id="10059555"):
    with open("kaggle.json") as credential:
        json_credential = json.loads(credential.read())
        os.environ["KAGGLE_USERNAME"] = json_credential["username"]
        os.environ["KAGGLE_KEY"] = json_credential["key"]
        os.environ["KAGGLE_TEAM_ID"] = team_id
    result = subprocess.check_output(["kaggle", "competitions", "submissions", "competitive-data-science-predict-future-sales"]).decode("utf-8")
    print(result)
