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
    df, rm_si_sn = tidy_data(os.path.join(uploaddir, csv_file))
    # print(rm_si_sn)
    meta_dct = generate_meta_dct(rm_si_sn)
    # print(f'meta dict: {meta_dct.keys()}')
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
    infile = os.path.join(cwd, infile)
    prs = Presentation(infile)
    rm_si_sn = False
    if 'signal_noise' and 'stain_index' not in plot_types_list:
        rm_si_sn = True
        # remove the 4th slide (stain index & signal-to-noise)
        print('removing stain index & signal noise slide')
        rId = prs.slides._sldIdLst[3].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[3]

    dct_props = update_dct_props(dct_props, table_content, rm_si_sn)
    exportdir = os.path.join(cwd, "exports")
    outfile = os.path.join(exportdir, stats_dct['timestamp'], outfile)
    # save outfile even if there is SN/SI or not
    prs.save(outfile)
    # open outfile now since it is most up-to-date
    prs = Presentation(outfile)
    # get number of slides for bottom function
    nbr_slides = len(prs.slides)
    for plot_type in dct_props.keys():
        insert_figure(outfile, outfile, dct_props[plot_type])
        print(outfile)
    # add regression table
    insert_regr_table(outfile, outfile, dct_props['regression'])
    # change plate number on first slide
    change_plate_nbr(outfile, outfile, stats_dct['platenum'])
    # add subtext
    for slide in range(1, nbr_slides):
        change_single_info_content(outfile, outfile, slide, stats_dct['subtext'])
    print('Completed inserting figues and tables into powerpoint slides')
