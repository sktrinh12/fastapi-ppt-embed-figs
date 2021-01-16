import shutil
from pptx_module import *

def save_file_to_disk(uploaded_file, uploaddir):
    temp_file = os.path.join(uploaddir, uploaded_file.filename)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
        print(f'uploaded: {temp_file}')
        return temp_file

def process_stats_file(csv_file, uploaddir, exportdir):
    rename_histo_scatter_imgs(uploaddir)
    df = tidy_data(os.path.join(uploaddir, csv_file))
    meta_dct = generate_meta_dct()
    # stats plots
    for plot_type in meta_dct.keys():
        create_stats_plot(df, meta_dct, plot_type, exportdir)

    # regression
    dfr = prepare_regr_df(df)
    xvals = output_time_xvals(dfr)
    regr_vals_dct = generate_regr_vals(xvals, dfr)
    stats_dct = output_stats(regr_vals_dct, dfr)
    stats_dct.update(regr_vals_dct)
    create_regr_plot(dfr, stats_dct, exportdir)
    print('completed processing of stats file')
    return list(meta_dct.keys()), stats_dct

def embed_ppt_slides(infile, outfile, plot_types_list, stats_dct, cwd, timestamp):
    dct_props = make_dct_props(plot_types_list, cwd, timestamp)
    table_content = make_table_content(stats_dct)
    dct_props = update_dct_props(dct_props, table_content)
    print(dct_props.keys())
    exportdir = os.path.join(cwd, "exports")
    first_run = True
    outfile = os.path.join(exportdir, stats_dct['timestamp'], outfile)
    for plot_type in dct_props.keys():
        if first_run:
            # the powerpoint blank template
            first_run = False
            file = os.path.join(cwd, infile)
        else:
            file = outfile
        print(file)
        insert_figure(file, outfile, dct_props[plot_type])
    # add regression table
    insert_regr_table(outfile, outfile, dct_props['regression'])
    # change plate number on first slide
    change_plate_nbr(outfile, outfile, stats_dct['platenum'])
    # add subtext
    for slide in range(1, 6):
        change_single_info_content(outfile, outfile, slide, stats_dct['subtext'])
    print('Completed inserting figues and tables into powerpoint slides')
