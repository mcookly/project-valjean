-- Click button script
function click_button(splash, sel)
    splash.images_enabled = false -- This may be redundant
    btn = splash:select(sel)
    if not btn then
        assert(splash:wait(splash.args.wait*2)) -- Wait a little longer...
        btn = splash:select(sel)
    end
    btn:mouse_click()
    assert(splash:wait(splash.args.wait))
end

function scan_meal(splash, index, meal_index)
    -- Click on right meal link (breakfast, lunch, dinner, brunch)
    -- and return contents with the appropriate label for easy parsing.
    click_button(splash, 'div.cbo_nn_menuTableDiv tr:nth-child(' .. index .. ') td.cbo_nn_menuCell > table > tbody > tr:nth-child(2) > td td:nth-child(' .. meal_index .. ') > a')
    return splash:html()
end

function main(splash, args)
    splash.images_enabled = false
    assert(splash:go(splash.args.url))
    assert(splash:wait(splash.args.wait))
    -- Navigate to meal list menu through 2 button clicks
    click_button(splash, splash.args.dh)
    click_button(splash, splash.args.fwd_btn)
    -- Click through and extract a snapshot of each meal's offerings
    local results = {}
    for meal_index, meal in ipairs(splash.args.meals) do
        results[meal] = scan_meal(splash, splash.args.index, meal_index)
        click_button(splash, '#btn_Back1')
    end

    return results
end